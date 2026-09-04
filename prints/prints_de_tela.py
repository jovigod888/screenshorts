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
        self.historico_arquivos = carregar_historico()

        # Configurações da Janela Principal (Aumentada um pouco para o histórico)
        self.title("Mnmst Capture")
        self.geometry("520x490")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.modo_selecao = "texto"

        # --- INTERFACE GRÁFICA ---

        # Título Discreto
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="COPIA & CAPTURA", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        self.label_titulo.pack(pady=(20, 10))

        # Painel de Botões
        self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes.pack(pady=5, padx=25, fill="x")

        # Botão 1: Tela Cheia
        self.btn_print_tela = ctk.CTkButton(
            self.frame_botoes,
            text="Tela Cheia",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=6,
            fg_color="#3A3B3C",
            hover_color="#4E5052",
            text_color="#FFFFFF",
            command=self.capturar_tela_cheia,
        )
        self.btn_print_tela.pack(side="left", expand=True, fill="x", padx=(0, 4))

        # Botão 2: Recortar Imagem
        self.btn_recorte_img = ctk.CTkButton(
            self.frame_botoes,
            text="Recortar Imagem",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=6,
            fg_color="#2C2D2E",
            hover_color="#3A3B3C",
            text_color="#E0E0E0",
            command=lambda: self.iniciar_selecao("imagem"),
        )
        self.btn_recorte_img.pack(side="left", expand=True, fill="x", padx=4)

        # Botão 3: Extrair Texto
        self.btn_ocr = ctk.CTkButton(
            self.frame_botoes,
            text="Extrair Texto",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=6,
            fg_color="#1F2021",
            hover_color="#2C2D2E",
            text_color="#E0E0E0",
            border_width=1,
            border_color="#3A3B3C",
            command=lambda: self.iniciar_selecao("texto"),
        )
        self.btn_ocr.pack(side="left", expand=True, fill="x", padx=(4, 0))

        # Caixa de texto
        self.caixa_texto = ctk.CTkTextbox(
            self, 
            height=120, 
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#1E1E1E",
            border_width=1,
            border_color="#2D2D2D"
        )
        self.caixa_texto.pack(pady=10, padx=25, fill="both", expand=True)

        # === SEÇÃO DO HISTÓRICO RECENTE ===
        self.label_hist_titulo = ctk.CTkLabel(
            self, 
            text="RECENTES (CLIQUE PARA ABRIR)", 
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#555555"
        )
        self.label_hist_titulo.pack(pady=(10, 5), padx=25, anchor="w")

        # Frame que vai segurar os botões do histórico
        self.frame_historico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_historico.pack(pady=(0, 10), padx=25, fill="x")

        # Mensagem padrão caso não tenha histórico
        self.label_vazio = ctk.CTkLabel(
        self.frame_historico, 
        text="Nenhuma captura recente.", 
        font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), 
        text_color="#444444"
        )
        self.label_vazio.pack(anchor="w", pady=5)

        # Label de Status
        self.label_status = ctk.CTkLabel(
            self, 
            text="Pronto.", 
            font=ctk.CTkFont(family="Segoe UI", size=11), 
            text_color="#777777"
        )
        self.label_status.pack(pady=(0, 15))

        # Atualiza a UI do histórico ao iniciar
        self.atualizar_interface_historico()

        # Intercepta o evento de fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)

    def fechar_aplicacao(self):
        """Salva o histórico antes de fechar."""
        salvar_historico(self.historico_arquivos)
        self.destroy()

    # --- ATUALIZAR INTERFACE DO HISTÓRICO ---
    def adicionar_ao_historico(self, nome_arquivo):
        """Adiciona um arquivo ao histórico e atualiza os botões na tela."""
        atualizar_historico(self.historico_arquivos, nome_arquivo)
        self.atualizar_interface_historico()

    def atualizar_interface_historico(self):
        # Limpa todos os widgets antigos de dentro do frame do histórico
        for widget in self.frame_historico.winfo_children():
            widget.destroy()

        if not self.historico_arquivos:
            self.label_vazio = ctk.CTkLabel(
                self.frame_historico, 
                text="Nenhuma captura recente.", 
                font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), 
                text_color="#444444"
            )
            self.label_vazio.pack(anchor="w", pady=5)

        # Recria os botões atualizados
        for arquivo in self.historico_arquivos:
            caminho_completo = os.path.join(self.pasta_destino, arquivo)
            
            # Cria um botão ultra minimalista para cada arquivo do histórico
            btn_item = ctk.CTkButton(
                self.frame_historico,
                text=arquivo,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                height=28,
                fg_color="#1A1A1A",
                hover_color="#2A2A2A",
                text_color="#888888",
                border_width=1,
                border_color="#252525",
                # O comando lambda abaixo força o botão a abrir o arquivo correto quando clicado
                command=lambda cp=caminho_completo: self.abrir_arquivo(cp)
            )
            btn_item.pack(fill="x", pady=2)

    def abrir_arquivo(self, caminho):
        """Abre o arquivo de imagem diretamente no visualizador do Windows."""
        try:
            if os.path.exists(caminho):
                os.startfile(caminho)
            else:
                self.label_status.configure(text="Arquivo não encontrado.", text_color="#CF6679")
        except Exception as e:
            self.label_status.configure(text=f"Erro ao abrir: {e}", text_color="#CF6679")

    # --- FUNÇÃO 1: PRINT TELA CHEIA ---
    def capturar_tela_cheia(self):
        self.withdraw()
        self.after(300, self._executar_print_cheio)

    def _executar_print_cheio(self):
        try:
            timestamp = datetime.now().strftime("%H-%M-%S")
            nome_arquivo = f"total_{timestamp}.png"
            caminho_salvamento = os.path.join(self.pasta_destino, nome_arquivo)

            print_tela = pyautogui.screenshot()
            print_tela.save(caminho_salvamento)

            self.deiconify()
            self.adicionar_ao_historico(nome_arquivo) # Atualiza histórico
            self.label_status.configure(text="Captura total salva.", text_color="#AAAAAA")
        except Exception as e:
            self.deiconify()
            self.label_status.configure(text=f"Erro: {e}", text_color="#CF6679")

    # --- FUNÇÃO AUXILIAR: COPIAR IMAGEM PARA O CLIPBOARD ---
    def copiar_imagem_para_clipboard(self, imagem):
        output = io.BytesIO()
        imagem.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        try:
            import win32clipboard  # pyright: ignore[reportMissingModuleSource]
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        except ImportError:
            print("Instale 'pip install pywin32' para enviar imagens direto pelo Ctrl+V.")

    # --- FUNÇÕES DE SELEÇÃO POR MOUSE ---
    def iniciar_selecao(self, modo):
        self.modo_selecao = modo
        self.withdraw()
        self.after(200, self.criar_tela_recorte)

    def criar_tela_recorte(self):
        self.print_fundo = pyautogui.screenshot()

        self.janela_recorte = tk.Toplevel()
        self.janela_recorte.attributes("-fullscreen", True)
        self.janela_recorte.attributes("-topmost", True)

        self.img_tk = ImageTk.PhotoImage(self.print_fundo)
        self.canvas = tk.Canvas(self.janela_recorte, cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.img_tk, anchor="nw")

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.ao_clicar)
        self.canvas.bind("<B1-Motion>", self.ao_arrastar)
        self.canvas.bind("<ButtonRelease-1>", self.ao_soltar)

    def ao_clicar(self, event):
        self.start_x = event.x
        self.start_y = event.y
        cor_borda = "#FFFFFF" if self.modo_selecao == "imagem" else "#AAAAAA"
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, 1, 1, outline=cor_borda, width=1, dash=(3, 3)
        )

    def ao_arrastar(self, event):
        cur_x, cur_y = event.x, event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def ao_soltar(self, event):
        end_x, end_y = event.x, event.y

        x1, y1, x2, y2, valido = retangulo_selecao(
            self.start_x, self.start_y, end_x, end_y
        )

        self.janela_recorte.destroy()

        if not valido:
            self.deiconify()
            return

        imagem_recortada = self.print_fundo.crop((x1, y1, x2, y2))
        
        if self.modo_selecao == "imagem":
            self.processar_apenas_imagem(imagem_recortada)
        else:
            self.processar_texto_ocr(imagem_recortada)

    def processar_apenas_imagem(self, imagem):
        try:
            timestamp = datetime.now().strftime("%H-%M-%S")
            nome_arquivo = f"recorte_{timestamp}.png"
            caminho_salvamento = os.path.join(self.pasta_destino, nome_arquivo)
            imagem.save(caminho_salvamento)

            self.copiar_imagem_para_clipboard(imagem)

            self.deiconify()
            self.adicionar_ao_historico(nome_arquivo) # Atualiza histórico
            self.label_status.configure(text="Imagem copiada e salva.", text_color="#AAAAAA")
        except Exception as e:
            self.deiconify()
            self.label_status.configure(text=f"Erro: {e}", text_color="#CF6679")

    def processar_texto_ocr(self, imagem):
        try:
            timestamp = datetime.now().strftime("%H-%M-%S")
            nome_arquivo = f"texto_{timestamp}.png"
            caminho_salvamento = os.path.join(self.pasta_destino, nome_arquivo)
            imagem.save(caminho_salvamento)

            img_np = np.array(imagem)
            resultado = self.leitor.readtext(img_np, detail=0)
            texto_final = texto_de_ocr(resultado)

            if texto_final != "[Nenhum texto detectado]":
                pyperclip.copy(texto_final)

            self.deiconify()
            self.caixa_texto.delete("1.0", tk.END)
            self.caixa_texto.insert("1.0", texto_final)

            self.adicionar_ao_historico(nome_arquivo) # Atualiza histórico
            self.label_status.configure(text="Texto extraído e copiado.", text_color="#AAAAAA")
        except Exception as e:
            self.deiconify()
            self.label_status.configure(text=f"Erro: {e}", text_color="#CF6679")


if __name__ == "__main__":
    app = SuperCapturaApp()
    app.mainloop()

