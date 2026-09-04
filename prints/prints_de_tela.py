import os
import sys
import json

# FORÇA O TERMINAL A USAR UTF-8
sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime
import io
import tkinter as tk
import customtkinter as ctk  # pyright: ignore[reportMissingImports]
import easyocr  # pyright: ignore[reportMissingImports]
import numpy as np # pyright: ignore[reportMissingImports]
import pyautogui  # pyright: ignore[reportMissingModuleSource]
import pyperclip
from PIL import Image, ImageTk  # pyright: ignore[reportMissingImports]

from capture_logic import atualizar_historico, retangulo_selecao, texto_de_ocr
from capture_logic import (
    atualizar_historico, 
    retangulo_selecao, 
    texto_de_ocr, 
    carregar_historico, 
    salvar_historico, 
    limpar_historico
)

# Configuração do tema visual (Minimalist Dark)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class SuperCapturaApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Inicializa o leitor de texto (OCR)
        print("Carregando leitor de texto (OCR)...")
        self.leitor = easyocr.Reader(["pt", "en"])
        print("[OK] Leitor pronto!")

        # Pasta de capturas
        self.pasta_destino = "capturas"
        if not os.path.exists(self.pasta_destino):
            os.makedirs(self.pasta_destino)

        # === LISTA PARA ARMAZENAR O HISTÓRICO ===
        self.historico_arquivos = []
        self.historico_arquivos = carregar_historico()

        # Configurações da Janela Principal (Aumentada um pouco para o histórico)
        self.title("Mnmst Capture")
        self.geometry("520x490")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.modo_selecao = "texto"

    def limpar_historico(self):
        self.historico_arquivos = []
        try:
            self.label_status.configure(text="Histórico limpo.", text_color="#AAAAAA")
        except Exception:
            pass

    def fechar_aplicacao(self):
        self.destroy()
        with open("historico.json", "w", encoding="utf-8") as f:
            json.dump(self.historico_arquivos, f)

    def carregar_historico(self):
        try:
            with open("historico.json", "r", encoding="utf-8") as f:
                self.historico_arquivos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.historico_arquivos = []

    def salvar_historico(self):
        with open("historico.json", "w", encoding="utf-8") as f:
            json.dump(self.historico_arquivos, f)


if __name__ == "__main__":
    app = SuperCapturaApp()
    app.mainloop()




    