# 📸 Mnmst Capture (Copia & Captura)

Um utilitário de captura de tela de alta performance com design minimalista, focado em produtividade. O aplicativo permite tirar prints da tela inteira, recortar áreas específicas diretamente para a área de transferência (`Ctrl + V`) e extrair textos de imagens em tempo real usando Inteligência Artificial (OCR).

---

## ✨ Funcionalidades

*   **📸 Tela Cheia:** Captura toda a área de trabalho instantaneamente.
*   **✂️ Recortar Imagem:** Seleção livre por clique e arraste com o mouse. A imagem recortada vai direto para a área de transferência (pronta para colar no Discord, WhatsApp, etc.).
*   **🔍 Extrair Texto (OCR):** Reconhece e extrai caracteres de qualquer imagem selecionada na tela, copiando o texto automaticamente e exibindo no painel de controle.
*   **📂 Pasta Dedicada (`/capturas`):** Todas as imagens geradas são salvas e organizadas automaticamente em uma pasta local sem poluir o diretório do script.
*   **📜 Histórico de Recentes:** Exibe os 3 últimos arquivos gerados no painel. Basta um clique sobre o nome do arquivo para abri-lo no visualizador padrão do Windows.
*   **🎨 Design Minimalista:** Interface escura integrada, inspirada nas diretrizes visuais do Notion e interfaces modernas da Apple.

---

## 🛠️ Pré-requisitos & Instalação

Antes de rodar o projeto, certifique-se de ter o Python instalado em sua máquina. Em seguida, instale as dependências necessárias executando o comando abaixo no terminal:

```bash
pip install customtkinter easyocr numpy pyautogui pyperclip pillow pywin32



