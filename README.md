# Mnmst Capture (Copia & Captura)

O **Mnmst Capture** é uma ferramenta desktop minimalista desenvolvida em Python para captura de tela inteligente e extração de texto em tempo real (OCR). Utilizando uma interface escura e moderna baseada em `customtkinter`, a aplicação permite realizar capturas de tela cheia, recortes de áreas específicas e cópia automatizada de textos diretamente para a área de transferência do sistema.

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

O projeto combina bibliotecas consagradas de automação, processamento de imagem e interfaces gráficas:

* **`customtkinter`**: Responsável pela interface gráfica de usuário (GUI) com design moderno, cantos arredondados e tema escuro nativo.
* **`pyautogui`**: Utilizada para capturar as resoluções de tela cheia (`screenshot`).
* **`easyocr`**: Motor de Inteligência Artificial para Reconhecimento Óptico de Caracteres (OCR), configurado para identificar textos em português (`pt`) e inglês (`en`).
* **`PIL (Pillow)`**: Manipulação, corte (`crop`) e renderização de imagens dentro do ambiente do Tkinter.
* **`pyperclip`**: Manipulação da área de transferência de texto do sistema operacional.
* **`numpy`**: Conversão de formato de imagem PIL para matrizes numéricas aceitas pelo EasyOCR.

---

## ⚙️ Arquitetura e Estrutura do Código (Ponto a Ponto)

Abaixo está o detalhamento de como cada bloco de código do script `prints_de_tela.py` funciona:

### 1. Inicialização e Configuração do Ambiente
* **Forçar UTF-8 (`sys.stdout.reconfigure`)**: Garante que o terminal não apresente erros de codificação de caracteres ao exibir logs com acentos no Windows.
* **Diretório de Salvamento**: Ao iniciar, o código verifica se a pasta `capturas/` existe. Caso contrário, ela é criada automaticamente para centralizar os arquivos gerados.
* **Carregamento do EasyOCR**: O motor de IA é carregado na inicialização (`self.leitor = easyocr.Reader(['pt', 'en'])`). Esse processo pode demorar alguns segundos na primeira execução porque valida os modelos linguísticos.

### 2. Interface Principal (`__init__`)
A janela possui dimensões fixas de `520x490` pixels e propriedade `-topmost` ativada, garantindo que o utilitário fique sempre visível sobre as outras janelas enquanto você trabalha.
* **Botões de Ação**: Três botões principais controlam os modos de operação (Tela Cheia, Recortar Imagem e Extrair Texto).
* **Caixa de Texto (`CTkTextbox`)**: Uma área com fonte monoespaçada (`Consolas`) onde os textos extraídos via OCR são exibidos para o usuário.
* **Histórico Recente**: Uma seção dinâmica que exibe até os 3 arquivos mais recentes gerados pela aplicação.

### 3. Mecanismo de Histórico Dinâmico
* **`adicionar_ao_historico(nome_arquivo)`**: Sempre que uma captura é feita, o nome do arquivo vai para o topo de uma lista. Se a lista passar de 3 itens, o mais antigo é descartado (`.pop()`). Os botões antigos são destruídos (`widget.destroy()`) e recriados em tempo de execução.
* **`abrir_arquivo(caminho)`**: Utiliza o método nativo do sistema operacional (`os.startfile`) para que, ao clicar em qualquer item do histórico, a imagem seja aberta instantaneamente no visualizador padrão do Windows.

### 4. Fluxo de Captura de Tela Cheia
Ao clicar em "Tela Cheia":
1. A janela do aplicativo se esconde (`self.withdraw()`) para não aparecer no print.
2. Aguarda-se `300ms` (`self.after`) para garantir que a interface sumiu por completo.
3. O `pyautogui.screenshot()` tira a foto da tela, salva na pasta com um *timestamp* (ex: `total_19-30-05.png`).
4. A janela reaparece (`self.deiconify()`) e o histórico atualiza.

### 5. Sistema de Recorte Personalizado (Canvas Transparente)
Ao escolher "Recortar Imagem" ou "Extrair Texto", o app executa uma técnica avançada de seleção de tela:
* Um print invisível do fundo é tirado e aplicado em uma nova janela em tela cheia sem bordas (`-fullscreen`).
* O cursor do mouse muda para uma mira de precisão (`cross`).
* **Eventos do Mouse**:
    * `<ButtonPress-1>` (Clique): Salva as coordenadas `x` e `y` iniciais.
    * `<B1-Motion>` (Arrastar): Desenha e atualiza um retângulo tracejado cinza ou branco na tela.
    * `<ButtonRelease-1>` (Soltar): Destrói a janela de recorte e calcula a área matemática (`x1, y1, x2, y2`) para recortar a imagem original utilizando a biblioteca Pillow.

### 6. Processamento de Imagem vs. Processamento de OCR
Após soltar o mouse, o comportamento muda baseado no modo selecionado:
* **Modo Imagem**: Salva o recorte na pasta e tenta enviar a imagem diretamente para a área de transferência usando a API do Windows (`win32clipboard`). Isso permite colar a imagem diretamente no Discord, WhatsApp ou Word usando `Ctrl+V`.
* **Modo Texto (OCR)**: Salva uma cópia de segurança da imagem, converte o recorte para uma matriz NumPy e passa para o `easyocr`. O texto processado é limpo, injetado na caixa de texto da interface e copiado automaticamente para a área de transferência do usuário.

### 7. Editor de Anotações (Setas, Texto, Marca-texto e Desfoque)
Antes de qualquer captura ir para o disco — tanto no "Tela Cheia" quanto no "Recortar Imagem" —, uma janela de edição é aberta com a imagem:
* **Seta**: clique e arraste para desenhar uma seta apontando para o que importa.
* **Texto**: clique no ponto desejado e digite o texto a ser inserido.
* **Marca-texto**: clique e arraste para sobrepor um retângulo translúcido colorido, como um marcador de texto.
* **Desfoque**: clique e arraste sobre a região sensível (senha, CPF, e-mail etc.) para pixelá-la antes de salvar.

A barra de ferramentas conta com seleção de cor (5 predefinidas ou uma cor customizada), **Desfazer** (também via `Ctrl+Z`) e os botões **Salvar** e **Cancelar** (ou tecla `Esc`, que descarta a captura sem gravar nada em disco). O modo "Extrair Texto" (OCR) não passa pelo editor, já que ali o objetivo é justamente ler o texto original da imagem.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o Python 3.10 ou superior instalado na sua máquina.

### 1. Instalação das Dependências
Abra o seu terminal ou prompt de comando e execute o comando abaixo para instalar todas as bibliotecas necessárias:

```bash
pip install customtkinter easyocr numpy pyautogui pyperclip pillow pywin32

## 2. Executando o Script

Navegue até a pasta onde está o arquivo `prints_de_tela.py` e execute o comando abaixo no terminal:

```bash
python prints_de_tela.py


```

### 📸​ captura de tela
Interface grafica 
![alt text](code.png)

print da aplicação
![alt text](<Captura de tela 2026-09-04 155820.png>)


### 📁 Estrutura de Pastas Gerada

Após realizar as primeiras capturas, a estrutura do seu projeto parecerá com isso:

```text
📂 Mnmst Capture/
├── 📄 prints_de_tela.py
└── 📂 capturas/
    ├── 🖼️ total_19-05-23.png
    ├── 🖼️ recorte_19-06-12.png
    └── 🖼️ texto_19-06-45.png


