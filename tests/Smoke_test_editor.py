import sys
from pathlib import Path

# Permite importar o módulo local independentemente do sistema operacional.
diretorio_teste = Path(__file__).resolve().parent
sys.path.insert(0, str(diretorio_teste))
sys.path.insert(0, str(diretorio_teste / "prints"))

import tkinter as tk
from tkinter import colorchooser, simpledialog
from types import SimpleNamespace

from PIL import Image
import customtkinter as ctk

# O módulo é disponibilizado pelo caminho local configurado acima; o analisador
# estático não consegue inferir esse caminho em tempo de execução.
import prints.editor_anotacoes as editor_anotacoes  # pyright: ignore[reportMissingImports]
from prints.editor_anotacoes import EditorDeAnotacoes  # pyright: ignore[reportMissingImports]

# Evita que askstring/askcolor tentem abrir diálogos interativos reais
editor_anotacoes.simpledialog.askstring = lambda *a, **k: "teste anotação"
editor_anotacoes.colorchooser.askcolor = lambda *a, **k: ((0, 200, 0), "#00C800")


def evento(x, y):
    return SimpleNamespace(x=x, y=y)


resultados = {"salvou": None, "cancelou": False}


def ao_salvar(imagem):
    resultados["salvou"] = imagem


def ao_cancelar():
    resultados["cancelou"] = True


root = ctk.CTk()
root.withdraw()

imagem_teste = Image.new("RGB", (300, 200), "white")

editor = EditorDeAnotacoes(root, imagem_teste, ao_salvar=ao_salvar, ao_cancelar=ao_cancelar)
root.update()
print("[OK] Janela criada. Escala:", editor.escala)

imagem_antes_seta = editor.imagem_atual.copy()
editor._selecionar_ferramenta("seta")
editor._ao_pressionar(evento(20, 20))
editor._ao_arrastar(evento(100, 20))
editor._ao_soltar(evento(100, 20))
root.update()
assert editor.imagem_atual.tobytes() != imagem_antes_seta.tobytes(), "seta não alterou a imagem"
print("[OK] Ferramenta seta aplicada")

imagem_antes_destaque = editor.imagem_atual.copy()
editor._selecionar_ferramenta("destaque")
editor._selecionar_cor("#FFD60A")
editor._ao_pressionar(evento(30, 60))
editor._ao_arrastar(evento(90, 100))
editor._ao_soltar(evento(90, 100))
root.update()
assert editor.imagem_atual.tobytes() != imagem_antes_destaque.tobytes(), "destaque não alterou a imagem"
print("[OK] Ferramenta marca-texto (destaque) aplicada")

editor.imagem_atual.putpixel((12, 12), (255, 0, 0))
editor.imagem_atual.putpixel((13, 12), (0, 0, 255))
imagem_antes_desfoque = editor.imagem_atual.copy()
editor._selecionar_ferramenta("desfoque")
editor._ao_pressionar(evento(10, 10))
editor._ao_arrastar(evento(30, 30))
editor._ao_soltar(evento(30, 30))
root.update()
assert editor.imagem_atual.tobytes() != imagem_antes_desfoque.tobytes(), "desfoque não alterou a imagem"
print("[OK] Ferramenta desfoque aplicada")

imagem_antes_texto = editor.imagem_atual.copy()
editor._selecionar_ferramenta("texto")
editor._ao_pressionar(evento(150, 150))  # dispara o askstring mockado
root.update()
assert editor.imagem_atual.tobytes() != imagem_antes_texto.tobytes(), "texto não alterou a imagem"
print("[OK] Ferramenta texto aplicada (askstring mockado)")

editor._abrir_seletor_cor()
assert editor.cor_atual == "#00C800", "seletor de cor customizado não aplicou a cor"
print("[OK] Seletor de cor customizado (askcolor mockado)")

imagem_antes_undo = editor.imagem_atual.copy()
editor._desfazer()
root.update()
assert editor.imagem_atual.tobytes() == imagem_antes_texto.tobytes(), "desfazer não restaurou o estado anterior"
assert editor.imagem_atual.tobytes() != imagem_antes_undo.tobytes()
print("[OK] Desfazer (undo) funcionando")

editor._salvar()
root.update()
assert resultados["salvou"] is not None, "callback ao_salvar não foi chamado"
print("[OK] Salvar chama o callback com a imagem final")

# segunda instância só para testar o cancelar
editor2 = EditorDeAnotacoes(root, imagem_teste, ao_salvar=ao_salvar, ao_cancelar=ao_cancelar)
root.update()
editor2._cancelar()
root.update()
assert resultados["cancelou"] is True, "callback ao_cancelar não foi chamado"
print("[OK] Cancelar chama o callback de cancelamento")

root.destroy()
print("\nTODOS OS TESTES DE GUI PASSARAM")