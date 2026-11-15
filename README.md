# 🎛 Estúdio do Cantor

**App tudo-em-um para cantores, músicos e criadores** — 100% local e offline, feito em Python + Tkinter.

| Função | O que faz |
|---|---|
| 🎤 **Separar voz × instrumental** | IA (Demucs) separa a voz da música localmente |
| 🎹 **Mudar o tom** | De −12 a +12 semitons mantendo a velocidade (ou estilo vinil) |
| 📝 **Legendas automáticas** | Transcreve áudio/vídeo e gera `.srt` + `.txt` (Whisper) |
| 💾 **Exportar MP3 / MP4** | Conversão com capa (planos MAX+) |
| 📺 **Postar no YouTube** | Upload direto pela API (plano ULTRA) |

---

## 💼 Modelo de negócio

| Plano | Preço | Libera |
|---|---|---|
| **Teste grátis** | R$ 0 (90 dias) | Tudo |
| **Modo restrito** | — (após o teste) | Funções simples, só 60s de áudio |
| **PLUS** | R$ 70/mês | Sem limites |
| **MAX** | R$ 100/mês | + Exportação/conversão (MP3/MP4) |
| **ULTRA** | R$ 140/mês | + Postagem direta no YouTube |

Licenças são **chaves mensais** geradas por você (veja `keygen.py`). Quando o cliente paga de novo, você gera uma nova chave com nova validade.

## 🚀 Instalação (do zero)

1. Instale o **Python 3.10+** (python.org) e o **FFmpeg**:
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
2. Abra o terminal nesta pasta e rode:
   - Windows: `instalar.bat`
   - macOS/Linux: `./install.sh`
3. Abra o app:
   - Windows: `executar.bat`
   - macOS/Linux: `./executar.sh`

## 💰 Receber pelo Mercado Pago

1. No app do Mercado Pago/site: **Criar link de pagamento** com o valor do plano (R$ 70 / R$ 100 / R$ 140)
2. Cliente paga por **Pix, cartão ou boleto** → o cai direto na sua conta MP
3. Você recebe a notificação por e-mail → roda `python keygen.py -t X -m 1` → envia a chave ao cliente
4. Para cobrança automática todo mês, use **Mercado Pago Assinaturas** (recurring) — o MP cobra o cliente sozinho e você só renova a chave

> Dica de taxas: Pix é o mais barato (~1,5%); cartão custa mais (~5%). Prefira deixar o Pix em destaque no link.

## 🔑 Fluxo de venda (passo a passo)

1. Publique o app no **GitHub** (veja `DEPLOY.md`) — os downloads de Windows/Mac/Linux são gerados automaticamente a cada versão.
2. Crie os **links de pagamento no Mercado Pago** e troque a constante `STORE_URL` no `app.py`.
3. Cliente paga → notificação chega no seu Mercado Pago → você roda:
   ```
   python keygen.py -t 3 -m 1
   ```
   (ULTRA por 1 mês; `-t 2` = MAX, `-m 12` = 12 meses)
4. Envie a chave; o cliente cola em **⭐ Ativar licença**.

## 📺 Configurar YouTube (plano ULTRA)

1. Crie um projeto em **console.cloud.google.com**
2. Ative a **YouTube Data API v3**
3. Credenciais → OAuth 2.0 (aplicativo Desktop) → baixe o JSON
4. Renomeie para `client_secret.json` e coloque na pasta do app

## ⚠️ Avisos honestos

- A chave é validada **localmente** (v1). Para proteção forte contra cracks, evolua para validação por servidor na v2.
- O teste de 90 dias fica salvo no PC do cliente; ser apagado reinicia o teste. Idem: servidor resolve na v2.
- Publicar conteúdo de terceiros no YouTube é responsabilidade do cliente (direitos autorais).
- Os modelos de IA (Demucs/Whisper) são open source (MIT) — vendê-los embrulhados num app é permitido; você vende o **produto**, não o modelo.

## 🗺️ Roadmap sugerido (v2)

- Fila de processamento (várias músicas de uma vez)
- Validação de licença por servidor
- Separar em 4 stems (bateria/baixo/outros)
- Filtro + eco para ensaio
- Versão demo: só 30s e sem exportação
