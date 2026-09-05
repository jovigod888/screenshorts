from PIL import Image

from prints.annotation_logic import (
    adicionar_texto,
    aplicar_desfoque,
    desenhar_destaque,
    desenhar_seta,
)


def test_seta_desenha_sem_alterar_imagem_original():
    imagem = Image.new("RGB", (100, 60), "white")

    resultado = desenhar_seta(imagem, 10, 30, 90, 30, cor="#FF3B30", espessura=4)

    assert resultado.getpixel((50, 30)) != (255, 255, 255)
    assert imagem.getpixel((50, 30)) == (255, 255, 255)  # original preservada


def test_destaque_mistura_cor_dentro_e_preserva_fora():
    imagem = Image.new("RGB", (100, 100), "white")

    resultado = desenhar_destaque(imagem, 20, 20, 80, 80, cor="#FFEB3B", opacidade=90)

    assert resultado.getpixel((50, 50)) != (255, 255, 255)  # dentro: mudou
    assert resultado.getpixel((5, 5)) == (255, 255, 255)  # fora: intacto


def test_desfoque_pixela_regiao_e_preserva_resto():
    imagem = Image.new("RGB", (40, 40), "white")
    imagem.putpixel((12, 12), (255, 0, 0))
    imagem.putpixel((13, 12), (0, 0, 255))

    resultado = aplicar_desfoque(imagem, 10, 10, 30, 30, intensidade=10)

    # pixels vizinhos que eram bem diferentes viram idênticos (mosaico)
    assert resultado.getpixel((12, 12)) == resultado.getpixel((13, 12))
    # fora da seleção, nada muda
    assert resultado.getpixel((0, 0)) == (255, 255, 255)
    # a imagem original não é alterada (função pura)
    assert imagem.getpixel((12, 12)) == (255, 0, 0)


def test_desfoque_normaliza_coordenadas_invertidas():
    imagem = Image.new("RGB", (40, 40), "white")
    imagem.putpixel((12, 12), (255, 0, 0))

    # arrasto "de trás para frente" (x2,y2 antes de x1,y1) deve funcionar igual
    resultado = aplicar_desfoque(imagem, 30, 30, 10, 10, intensidade=10)

    assert resultado.size == imagem.size
    assert resultado.getpixel((0, 0)) == (255, 255, 255)


def test_adicionar_texto_altera_pixels_na_regiao():
    imagem = Image.new("RGB", (200, 60), "white")

    resultado = adicionar_texto(imagem, 10, 10, "Oi", cor="#000000", tamanho=24)

    regiao_antes = imagem.crop((10, 10, 80, 40)).tobytes()
    regiao_depois = resultado.crop((10, 10, 80, 40)).tobytes()
    assert regiao_antes != regiao_depois
