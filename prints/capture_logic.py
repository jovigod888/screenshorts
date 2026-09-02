"""Lógica pura da captura — sem GUI, para testes em CI."""

import json


def atualizar_historico(historico, imagem, limite=3):
    """Insere o arquivo no início e mantém só os N mais recentes."""
    historico.insert(0, imagem)
    if len(historico) > limite:
        historico.pop()
    return historico


def retangulo_selecao(start_x, start_y, end_x, end_y, min_tamanho=5):
    """Normaliza o retângulo do mouse e indica se a área é grande o bastante."""
    x1 = min(start_x, end_x)
    y1 = min(start_y, end_y)
    x2 = max(start_x, end_x)
    y2 = max(start_y, end_y)
    valido = (x2 - x1) >= min_tamanho and (y2 - y1) >= min_tamanho
    return x1, y1, x2, y2, valido


def texto_de_ocr(resultado):
    """Junta as linhas do EasyOCR e trata detecção vazia."""
    texto_final = "\n".join(resultado)
    if not texto_final.strip():
        return "[Nenhum texto detectado]"
    return texto_final


def salvar_historico(historico):
    with open("historico.json", "w") as f:
        json.dump(historico, f)


def carregar_historico():
    try:
        with open("historico.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def limpar_historico():
    with open("historico.json", "w") as f:
        json.dump([], f)


def adicionar_ao_historico(historico, imagem):
    historico.append(imagem)
    salvar_historico(historico)
    return historico


def remover_do_historico(historico, imagem):
    historico.remove(imagem)
    salvar_historico(historico)
    return historico
