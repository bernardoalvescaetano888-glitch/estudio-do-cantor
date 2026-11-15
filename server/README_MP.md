# 💸 Integração Mercado Pago — entrega automática de licenças

Quando o cliente paga, o Mercado Pago chama seu servidor → o servidor busca o pagamento na API → **gera a chave e envia por e-mail em segundos**, e registra tudo em `vendas.json`.

```
Cliente paga (link MP) → MP → POST /webhook → MP API (v1/payments) → chave → e-mail ✉
```

## 1. Pegar credenciais no Mercado Pago

1. Acesse **developers.mercadopago.com** → entre com sua conta
2. "Sua integração" → "Credenciais" → copie o **Access Token de produção** (`APP_USR-...`)
3. ⚠️ **Nunca coloque o token no código nem no repositório** — ele fica só no `.env`

## 2. Configurar o servidor

```bash
cd server
pip install -r requirements.txt
copy .env.example .env       # Windows  (Linux/Mac: cp .env.example .env)
# edite o .env: MP_ACCESS_TOKEN, e-mail (Gmail: senha de app de 16 letras)
python mp_server.py          # sobe em http://localhost:5000
```

## 3. Colocar o servidor online (grátis)

- **Render.com** (recomendado): novo "Web Service" → conecte seu repo GitHub → comando: `pip install -r server/requirements.txt && python server/mp_server.py` → copie a URL pública
- Alternativa: Railway, Fly.io, PythonAnywhere
- Teste local: `ngrok http 5000` gera uma URL temporária

## 4. Conectar o webhook

1. Em developers.mercadopago.com → Sua integração → **Webhooks** →
   URL: `https://SEU-SERVIDOR/webhook` → evento: **pagamentos (payments)**
2. Ou informe a URL ao criar os links (passo 5) com `--webhook`

## 5. Criar os 3 links de pagamento

```bash
python mp_links.py --webhook https://SEU-SERVIDOR.onrender.com/webhook
```

Imprime os links PLUS/MAX/ULTRA prontos pra colocar na bio. Cada link já aponta pro seu webhook.

## 6. Testar sem pagar de verdade

- No painel MP, copie o **Access Token de TESTE** para o `.env`
- Cadastre 2 usuários de teste (vendedor/comprador) na sua integração
- Pague o link com cartão de teste → veja o log do servidor e o e-mail chegar
- Teste manual de um pagamento real existente:
  ```
  python deliver.py 1234567890
  ```

## Segurança e limites (honestidade)

| Ponto | Situação |
|---|---|
| Token MP | No `.env` do servidor, nunca no repo ✅ |
| `.env` / `vendas.json` | Ignorados pelo Git ✅ |
| Webhook de origem | v1 não valida assinatura; **v2**: validar header `x-signature` do MP |
| Planos com desconto/cupom | Ajuste `PRICE_TIERS` em `mp_api.py` |
| Renovação | Chave de 31 dias; cliente assinante recebe nova chave todo mês (assinaturas MP) |
