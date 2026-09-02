from capture_logic import atualizar_historico, retangulo_selecao, texto_de_ocr


def test_historico_insere_no_inicio():
    historico = ["antigo.png"]
    atualizar_historico(historico, "novo.png")
    assert historico == ["novo.png", "antigo.png"]


def test_historico_mantem_no_maximo_tres():
    historico = ["a.png", "b.png", "c.png"]
    atualizar_historico(historico, "d.png")
    assert historico == ["d.png", "a.png", "b.png"]
    assert len(historico) == 3


def test_retangulo_normaliza_arraste_invertido():
    x1, y1, x2, y2, valido = retangulo_selecao(100, 80, 10, 20)
    assert (x1, y1, x2, y2) == (10, 20, 100, 80)
    assert valido is True


def test_retangulo_pequeno_e_invalido():
    *_, valido = retangulo_selecao(10, 10, 12, 12)
    assert valido is False


def test_ocr_junta_linhas():
    assert texto_de_ocr(["Olá", "mundo"]) == "Olá\nmundo"


def test_ocr_vazio_mostra_aviso():
    assert texto_de_ocr([]) == "[Nenhum texto detectado]"
    assert texto_de_ocr(["   "]) == "[Nenhum texto detectado]"
