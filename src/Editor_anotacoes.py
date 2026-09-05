"""Editor de anotações exibido logo após a captura, antes de salvar.

Permite desenhar setas, adicionar texto, marcar (highlight) e borrar
(desfoque) trechos da imagem — por exemplo, para ocultar senhas, dados
pessoais ou qualquer informação sensível antes de salvar ou compartilhar
a captura.
"""

import importlib.util
import pathlib
import tkinter as tk
from tkinter import colorchooser, simpledialog

import customtkinter as ctk  # pyright: ignore[reportMissingImports]
from PIL import ImageTk  # pyright: ignore[reportMissingImports]


def _carregar_annotation_logic():
    """Carrega o módulo de lógica de anotação mesmo quando o arquivo é
    executado fora de um pacote Python."""
    caminho = pathlib.Path(__file__).with_name("annotation_logic.py")
    if not caminho.exists():
        raise FileNotFoundError(f"Módulo de anotação não encontrado em: {caminho}")

    spec = importlib.util.spec_from_file_location("annotation_logic", caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível criar o loader para {caminho}")

    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


annotation_logic = _carregar_annotation_logic()

adicionar_texto = annotation_logic.adicionar_texto
aplicar_desfoque = annotation_logic.aplicar_desfoque
desenhar_destaque = annotation_logic.desenhar_destaque
desenhar_seta = annotation_logic.desenhar_seta

CORES_PRESET = ("#FF3B30", "#FFD60A", "#34C759", "#0A84FF", "#FFFFFF")

ROTULOS_FERRAMENTAS = {
    "seta": "↗ Seta",
    "texto": "T  Texto",
    "destaque": "▮ Marca-texto",
    "desfoque": "▦ Desfoque",
}

LARGURA_MINIMA_JANELA = 1100


class EditorDeAnotacoes(tk.Toplevel):
    """Janela modal de anotação.

    Uso: `EditorDeAnotacoes(master, imagem, ao_salvar=..., ao_cancelar=...)`.
    `ao_salvar(imagem_final)` é chamado quando o usuário clica em "Salvar".
    `ao_cancelar()` é chamado quando ele cancela (botão, Esc ou fechar a
    janela) — a captura é descartada e nada é salvo em disco.
    """

    def __init__(self, master, imagem, ao_salvar, ao_cancelar):
        super().__init__(master)
        self.ao_salvar = ao_salvar
        self.ao_cancelar = ao_cancelar

        self.imagem_original = imagem.convert("RGB")
        self.imagem_atual = self.imagem_original.copy()
        self.pilha_desfazer = []

        largura_img = self.imagem_original.width
        self.ferramenta = "seta"
        self.cor_atual = CORES_PRESET[0]
        self.espessura = max(4, largura_img // 300)
        self.tamanho_fonte = max(18, largura_img // 50)
        self.intensidade_desfoque = 12

        self.title("Anotar captura")
        self.configure(bg="#151516")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._cancelar)
        self.bind("<Escape>", lambda evento: self._cancelar())
        self.bind("<Control-z>", lambda evento: self._desfazer())

        self._montar_barra_ferramentas()
        self._montar_canvas()
        self._redesenhar()

        self.update_idletasks()
        self.grab_set()
        self.focus_force()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _montar_barra_ferramentas(self):
        self.barra = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=0)
        self.barra.pack(side="top", fill="x")

        self.botoes_ferramentas = {}
        for nome, rotulo in ROTULOS_FERRAMENTAS.items():
            botao = ctk.CTkButton(
                self.barra,
                text=rotulo,
                width=112,
                height=32,
                corner_radius=6,
                fg_color="#3A3B3C" if nome == self.ferramenta else "#2C2D2E",
                hover_color="#4E5052",
                text_color="#FFFFFF" if nome == self.ferramenta else "#E0E0E0",
                command=lambda n=nome: self._selecionar_ferramenta(n),
            )
            botao.pack(side="left", padx=(10, 4), pady=8)
            self.botoes_ferramentas[nome] = botao

        self.swatches = {}
        for cor in CORES_PRESET:
            swatch = ctk.CTkButton(
                self.barra,
                text="",
                width=22,
                height=22,
                corner_radius=11,
                fg_color=cor,
                hover_color=cor,
                border_width=2,
                border_color="#FFFFFF" if cor == self.cor_atual else "#1E1E1E",
                command=lambda c=cor: self._selecionar_cor(c),
            )
            swatch.pack(side="left", padx=2, pady=8)
            self.swatches[cor] = swatch

        ctk.CTkButton(
            self.barra,
            text="Outra cor",
            width=90,
            height=32,
            corner_radius=6,
            fg_color="#2C2D2E",
            hover_color="#4E5052",
            command=self._abrir_seletor_cor,
        ).pack(side="left", padx=(6, 10), pady=8)

        ctk.CTkButton(
            self.barra,
            text="Desfazer",
            width=90,
            height=32,
            corner_radius=6,
            fg_color="#2C2D2E",
            hover_color="#4E5052",
            command=self._desfazer,
        ).pack(side="right", padx=(4, 10), pady=8)
        ctk.CTkButton(
            self.barra,
            text="Cancelar",
            width=90,
            height=32,
            corner_radius=6,
            fg_color="#2C2D2E",
            hover_color="#CF6679",
            command=self._cancelar,
        ).pack(side="right", padx=4, pady=8)
        ctk.CTkButton(
            self.barra,
            text="Salvar",
            width=90,
            height=32,
            corner_radius=6,
            fg_color="#0A84FF",
            hover_color="#3AA0FF",
            command=self._salvar,
        ).pack(side="right", padx=4, pady=8)

    def _montar_canvas(self):
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        margem, altura_barra = 80, 64
        largura_img, altura_img = self.imagem_original.size

        self.escala = min(
            1.0,
            (largura_tela - margem) / largura_img,
            (altura_tela - margem - altura_barra) / altura_img,
        )

        largura_canvas = max(1, int(largura_img * self.escala))
        altura_canvas = max(1, int(altura_img * self.escala))

        self.canvas = tk.Canvas(
            self,
            cursor="tcross",
            width=largura_canvas,
            height=altura_canvas,
            highlightthickness=0,
            bg="#000000",
        )
        self.canvas.pack(side="top")

        self.canvas.bind("<ButtonPress-1>", self._ao_pressionar)
        self.canvas.bind("<B1-Motion>", self._ao_arrastar)
        self.canvas.bind("<ButtonRelease-1>", self._ao_soltar)

        self._item_preview = None
        self._inicio = None

        largura_janela = max(largura_canvas, LARGURA_MINIMA_JANELA)
        altura_janela = altura_canvas + altura_barra
        x_pos = max(0, (largura_tela - largura_janela) // 2)
        y_pos = max(0, (altura_tela - altura_janela) // 2)
        self.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")

    # ------------------------------------------------------------------
    # Seleção de ferramenta e cor
    # ------------------------------------------------------------------

    def _selecionar_ferramenta(self, nome):
        self.ferramenta = nome
        for n, botao in self.botoes_ferramentas.items():
            ativo = n == nome
            botao.configure(
                fg_color="#3A3B3C" if ativo else "#2C2D2E",
                text_color="#FFFFFF" if ativo else "#E0E0E0",
            )

    def _selecionar_cor(self, cor):
        self.cor_atual = cor
        for c, swatch in self.swatches.items():
            swatch.configure(border_color="#FFFFFF" if c == cor else "#1E1E1E")

    def _abrir_seletor_cor(self):
        cor = colorchooser.askcolor(color=self.cor_atual, title="Escolher cor", parent=self)
        if cor and cor[1]:
            self._selecionar_cor(cor[1])

    # ------------------------------------------------------------------
    # Interação do mouse no canvas
    # ------------------------------------------------------------------

    def _para_imagem(self, x, y):
        """Converte coordenadas do canvas (que pode estar em escala reduzida
        para caber na tela) para coordenadas reais em pixels da imagem."""
        return int(x / self.escala), int(y / self.escala)

    def _ao_pressionar(self, evento):
        if self.ferramenta == "texto":
            self._inicio = None
            texto = simpledialog.askstring("Texto", "Digite o texto:", parent=self)
            if texto:
                x_img, y_img = self._para_imagem(evento.x, evento.y)
                self._aplicar_operacao(
                    adicionar_texto,
                    x_img,
                    y_img,
                    texto,
                    cor=self.cor_atual,
                    tamanho=self.tamanho_fonte,
                )
            return

        self._inicio = (evento.x, evento.y)

    def _ao_arrastar(self, evento):
        if self._inicio is None:
            return
        if self._item_preview is not None:
            self.canvas.delete(self._item_preview)

        x0, y0 = self._inicio
        if self.ferramenta == "seta":
            self._item_preview = self.canvas.create_line(
                x0, y0, evento.x, evento.y,
                fill=self.cor_atual, width=2, dash=(4, 2), arrow="last",
            )
        else:
            self._item_preview = self.canvas.create_rectangle(
                x0, y0, evento.x, evento.y,
                outline=self.cor_atual, width=2, dash=(4, 2),
            )

    def _ao_soltar(self, evento):
        if self._inicio is None:
            return
        if self._item_preview is not None:
            self.canvas.delete(self._item_preview)
            self._item_preview = None

        x0, y0 = self._inicio
        self._inicio = None

        if abs(evento.x - x0) < 3 and abs(evento.y - y0) < 3:
            return  # clique sem arraste perceptível: ignora

        x1, y1 = self._para_imagem(x0, y0)
        x2, y2 = self._para_imagem(evento.x, evento.y)

        if self.ferramenta == "seta":
            self._aplicar_operacao(
                desenhar_seta, x1, y1, x2, y2,
                cor=self.cor_atual, espessura=self.espessura,
            )
        elif self.ferramenta == "destaque":
            self._aplicar_operacao(desenhar_destaque, x1, y1, x2, y2, cor=self.cor_atual)
        elif self.ferramenta == "desfoque":
            self._aplicar_operacao(
                aplicar_desfoque, x1, y1, x2, y2, intensidade=self.intensidade_desfoque
            )

    # ------------------------------------------------------------------
    # Aplicação de operações / desfazer / redesenho
    # ------------------------------------------------------------------

    def _aplicar_operacao(self, funcao, *args, **kwargs):
        self.pilha_desfazer.append(self.imagem_atual.copy())
        self.imagem_atual = funcao(self.imagem_atual, *args, **kwargs)
        self._redesenhar()

    def _desfazer(self):
        if not self.pilha_desfazer:
            return
        self.imagem_atual = self.pilha_desfazer.pop()
        self._redesenhar()

    def _redesenhar(self):
        largura, altura = self.imagem_atual.size
        exibicao = self.imagem_atual.resize(
            (max(1, int(largura * self.escala)), max(1, int(altura * self.escala)))
        )
        self._imagem_tk = ImageTk.PhotoImage(exibicao)
        self.canvas.delete("conteudo")
        self.canvas.create_image(0, 0, image=self._imagem_tk, anchor="nw", tags="conteudo")

    # ------------------------------------------------------------------
    # Finalização
    # ------------------------------------------------------------------

    def _salvar(self):
        imagem_final = self.imagem_atual
        self.grab_release()
        self.destroy()
        self.ao_salvar(imagem_final)

    def _cancelar(self):
        self.grab_release()
        self.destroy()
        self.ao_cancelar()