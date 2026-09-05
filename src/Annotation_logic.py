"""Lógica pura de anotação de imagens — sem GUI, para permitir testes em CI.

Cada função recebe uma imagem PIL e devolve uma NOVA imagem com a anotação
já aplicada (a imagem recebida nunca é alterada). Isso deixa o "desfazer"
(undo) do editor simples — basta guardar as versões anteriores — e permite
testar cada efeito isoladamente, sem precisar abrir nenhuma janela.
"""

import math

from PIL import Image, ImageColor, ImageDraw, ImageFont


def _ordenar_retangulo(x1, y1, x2, y2):
    """Normaliza para x1<x2 e y1<y2 e garante uma área mínima de 1x1."""
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    x2 = max(x2, x1 + 1)
    y2 = max(y2, y1 + 1)
    return x1, y1, x2, y2


def _carregar_fonte(tamanho):
    """Tenta carregar uma fonte TrueType legível; usa a fonte padrão do
    Pillow como último recurso, caso nenhuma esteja disponível no sistema."""
    for nome in ("arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def desenhar_seta(imagem, x1, y1, x2, y2, cor="#FF3B30", espessura=4):
    """Desenha uma seta indo do ponto (x1, y1) até (x2, y2)."""
    resultado = imagem.convert("RGB").copy()
    desenho = ImageDraw.Draw(resultado)

    desenho.line((x1, y1, x2, y2), fill=cor, width=espessura)

    # Ponta da seta: duas linhas anguladas "voltando" a partir do ponto final
    angulo = math.atan2(y2 - y1, x2 - x1)
    tamanho_ponta = max(12, espessura * 4)
    abertura = math.radians(28)

    for sinal in (1, -1):
        ponta_x = x2 - tamanho_ponta * math.cos(angulo - sinal * abertura)
        ponta_y = y2 - tamanho_ponta * math.sin(angulo - sinal * abertura)
        desenho.line((x2, y2, ponta_x, ponta_y), fill=cor, width=espessura)

    return resultado


def desenhar_destaque(imagem, x1, y1, x2, y2, cor="#FFEB3B", opacidade=90):
    """Sobrepõe um retângulo translúcido na região (efeito marca-texto)."""
    x1, y1, x2, y2 = _ordenar_retangulo(x1, y1, x2, y2)
    base = imagem.convert("RGBA")

    camada = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(camada).rectangle(
        (x1, y1, x2, y2), fill=(*ImageColor.getrgb(cor), opacidade)
    )

    return Image.alpha_composite(base, camada).convert("RGB")


def aplicar_desfoque(imagem, x1, y1, x2, y2, intensidade=12):
    """Pixela (mosaico) a região selecionada da imagem.

    Em vez de um desfoque gaussiano simples — que em alguns casos pode ser
    parcialmente revertido —, a região é reduzida e depois ampliada de volta
    sem suavização. O resultado são blocos sólidos que escondem de forma
    bem mais confiável senhas, números de documentos e outros dados
    sensíveis que aparecem na captura.
    """
    x1, y1, x2, y2 = _ordenar_retangulo(x1, y1, x2, y2)
    x1, y1 = max(x1, 0), max(y1, 0)
    x2, y2 = min(x2, imagem.width), min(y2, imagem.height)

    resultado = imagem.convert("RGB").copy()
    regiao = resultado.crop((x1, y1, x2, y2))
    largura, altura = regiao.size

    intensidade = max(2, intensidade)
    pequena = regiao.resize(
        (max(1, largura // intensidade), max(1, altura // intensidade)),
        Image.BILINEAR,
    )
    mosaico = pequena.resize((largura, altura), Image.NEAREST)

    resultado.paste(mosaico, (x1, y1))
    return resultado


def adicionar_texto(imagem, x, y, texto, cor="#FFFFFF", tamanho=22):
    """Escreve um texto na posição indicada, com contorno escuro para manter
    a legibilidade sobre qualquer fundo da captura."""
    resultado = imagem.convert("RGB").copy()
    desenho = ImageDraw.Draw(resultado)
    fonte = _carregar_fonte(tamanho)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                desenho.text((x + dx, y + dy), texto, font=fonte, fill="#000000")
    desenho.text((x, y), texto, font=fonte, fill=cor)

    return resultado