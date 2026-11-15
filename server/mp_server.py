# -*- coding: utf-8 -*-
"""
mp_server.py — Servidor de entrega automática de licenças (Mercado Pago)

Fluxo: cliente paga -> MP chama POST /webhook -> buscamos o pagamento na API
-> geramos a chave -> enviamos por e-mail -> registramos em vendas.json

Executar:  python mp_server.py        (produção, via waitress)
"""
import os
import json
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

from flask import Flask, request, jsonify, Response   # noqa: E402
from mp_api import get_payment                       # noqa: E402
from deliver import process_payment                  # noqa: E402
from pix import PLANS, create_pix                    # noqa: E402

app = Flask(__name__)

LEDGER = os.path.join(HERE, "vendas.json")


def _key_from_ledger(pid):
    try:
        with open(LEDGER, "r", encoding="utf-8") as f:
            for sale in json.load(f):
                if str(sale.get("id")) == str(pid) and sale.get("chave"):
                    return sale["chave"]
    except Exception:
        pass
    return None



@app.get("/health")
def health():
    return jsonify(ok=True, app="estudio-do-cantor")


@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True) or {}
    # MP envia {"type"/"topic": "payment", "data"/"resource": {"id": ...}}
    topic = data.get("type") or data.get("topic") or request.args.get("topic")
    pid = (data.get("data") or {}).get("id") or data.get("resource") \
        or request.args.get("id") or request.args.get("data.id")

    if not pid or str(topic) != "payment":
        return jsonify(ok=True, ignored=True)

    try:
        payment = get_payment(str(pid))
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

    result = process_payment(payment)
    print(f"[webhook] {result}")
    return jsonify(ok=True, result=result)


# ------------------------------------------------------------------ Pix QR
PAGE = """<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pagamento Pix — Estúdio do Cantor</title>
<style>
 body{background:#0f1117;color:#e8eaf0;font-family:system-ui,Segoe UI,sans-serif;
      display:flex;flex-direction:column;align-items:center;padding:24px;margin:0}
 h1{font-size:1.2em;color:#3ddc97;margin:.2em}
 .plan{background:#1c2130;padding:10px 22px;border-radius:12px;font-size:1.05em}
 img{width:min(320px,80vw);border-radius:12px;background:#fff;padding:12px;margin:14px}
 .hint{color:#8a93a5;font-size:.9em;text-align:center;max-width:340px}
 textarea{width:min(340px,90vw);height:70px;background:#10131b;color:#3ddc97;
          border:1px solid #2a3040;border-radius:10px;padding:10px;font-size:.8em}
 button{margin:10px;background:#3ddc97;border:0;padding:12px 26px;border-radius:12px;
        font-weight:700;font-size:1em;cursor:pointer}
 #status{margin-top:14px;color:#ffb454}
 #lic{margin-top:14px;background:#1c2130;border:1px solid #3ddc97;border-radius:12px;
      padding:16px;text-align:center;max-width:360px}
 code{background:#10131b;padding:6px 10px;border-radius:8px;display:inline-block;
      margin:8px 0;font-size:.95em;color:#3ddc97;word-break:break-all}
 a{color:#5aa7ff}
</style></head><body>
<h1>🎛 Estúdio do Cantor</h1>
<p class="plan">__PLAN_NAME__ — R$ __AMOUNT__ / mês</p>
<img alt="QR Code Pix" src="data:image/png;base64,__QR64__">
<p class="hint">Abra o app do seu banco ou o Mercado Pago → <b>Pix → pagar com QR</b>.
Prefere copiar? Use o código abaixo.</p>
<textarea readonly id="copia">__QR_PAYLOAD__</textarea>
<button onclick="navigator.clipboard.writeText(document.getElementById('copia').value);this.textContent='✅ Copiado!'">📋 Copiar código Pix</button>
<div id="status">⏳ Aguardando pagamento… (a página atualiza sozinha)</div>
<div id="lic" hidden>🎉 <b>Pagamento confirmado!</b><br>
Sua chave de licença:<br><code id="key">…</code><br>
Abra o app → ⭐ Ativar licença → cole aqui.<br>
<small>Também enviamos a chave por e-mail.</small></div>
<script>
const PID=__PID__;
const t=setInterval(async()=>{try{
 const r=await fetch('/status/'+PID); const j=await r.json();
 if(j.status==='approved'){clearInterval(t);
  document.getElementById('status').hidden=true;
  document.getElementById('lic').hidden=false;
  document.getElementById('key').textContent=j.chave||'enviamos para seu e-mail';}
}catch(e){}},3000);
</script></body></html>"""


@app.get("/fixo")
def fixo():
    """QRs estáticos do Mercado Pago (cadastrados pelo vendedor no app MP).
    Recebem o dinheiro direto, mas NÃO entregam chave automática — entrega manual."""
    from flask import url_for
    items = ""
    for t, (n, v) in sorted(PLANS.items()):
        fname = {1: "pix_plus_70.png", 2: "pix_max_100.png", 3: "pix_ultra_140.png"}[t]
        items += (
            f"<div style='background:#1c2130;border-radius:14px;padding:18px;"
            f"margin:14px;max-width:340px;text-align:center'>"
            f"<h2 style='color:#3ddc97;margin:6px'>{n} — R$ {v}/mês</h2>"
            f"<img src='/static/qr/{fname}' style='width:100%;border-radius:10px;background:#fff'>"
            f"<p style='color:#8a93a5;font-size:.85em'>Pague escaneando com o app do seu banco "
            f"(Mercado Pago → Pix → ler QR). Depois envie o comprovante pelo WhatsApp "
            f"para receber sua chave do app ⭐ Ativar licença.</p></div>")
    return Response(
        "<html lang=pt-BR><meta charset=utf-8><meta name=viewport "
        "content='width=device-width,initial-scale=1'><title>Pagamento Pix — Estúdio do Cantor</title>"
        "<body style='background:#0f1117;color:#e8eaf0;font-family:system-ui;"
        "display:flex;flex-direction:column;align-items:center;padding:24px'>"
        "<h1 style='color:#3ddc97'>🎛 Estúdio do Cantor</h1>"
        "<p>Pagamento via <b>Pix QR fixo</b> (Mercado Pago)</p>" + items +
        "<a href='/plans' style='color:#5aa7ff'>← Voltar aos planos (com entrega automática)</a>"
        "</body></html>", content_type="text/html; charset=utf-8")


# ------------------------------------------------------------------ downloads diretos
# O cliente baixa pela SUA página, sem ver o GitHub por trás:
# /dl/<nome> -> redireciona (302) para o arquivo da Release
_DL = {
    "windows":         "https://github.com/bernardoalvescaetano888-glitch/estudio-download/releases/latest/download/EstudioDoCantor-Setup.exe",
    "windows-portatil":"https://github.com/bernardoalvescaetano888-glitch/estudio-download/releases/latest/download/EstudioDoCantor-Portable-Windows.zip",
    "macos":           "https://github.com/bernardoalvescaetano888-glitch/estudio-download/releases/latest/download/EstudioDoCantor.dmg",
    "linux":           "https://github.com/bernardoalvescaetano888-glitch/estudio-download/releases/latest/download/estudiodocantor.deb",
    "linux-portatil":  "https://github.com/bernardoalvescaetano888-glitch/estudio-download/releases/latest/download/EstudioDoCantor-Portable-Linux.tar.gz",
    "fonte":           "https://github.com/bernardoalvescaetano888-glitch/estudio-download/archive/refs/heads/main.zip",
}


@app.get("/dl/<nome>")
def dl(nome):
    destino = _DL.get(nome)
    if not destino:
        return Response("Download inexistente", status=404)
    return Response(status=302, headers={"Location": destino})


@app.get("/")
@app.get("/download")
def download_site():
    """Site de download (index.html do repo estudio-download)."""
    page = os.path.join(HERE, "download.html")
    if os.path.exists(page):
        with open(page, "r", encoding="utf-8") as f:
            return Response(f.read(), content_type="text/html; charset=utf-8")
    return Response("<meta charset=utf-8><h1>🎛 Estúdio do Cantor</h1>"
                    "<p>Sistema de licenças no ar. Use /plans para comprar.</p>",
                    content_type="text/html; charset=utf-8")


@app.get("/plans")
def plans():
    items = "".join(
        f'<li><a href="/buy/{t}">{n} — R$ {v}/mês</a></li>'
        for t, (n, v) in sorted(PLANS.items()))
    return Response(
        "<html lang=pt-BR><meta charset=utf-8><title>Planos — Estúdio do Cantor></title>"
        "<body style='background:#0f1117;color:#e8eaf0;font-family:system-ui;"
        "display:flex;flex-direction:column;align-items:center;padding-top:60px'>"
        "<h1 style='color:#3ddc97'>🎛 Estúdio do Cantor</h1>"
        "<p>Escolha seu plano (licença mensal, pagamento via Pix):</p>"
        f"<ul style='list-style:none;padding:0;text-align:center'>{items}</ul>"
        "<p style='color:#8a93a5'><a href='/fixo' style='color:#ffb454'>📄 Pagar com QR fixo "
        "(entrega manual pelo WhatsApp)</a></p>"
        "</body></html>", content_type="text/html; charset=utf-8")


@app.get("/buy/<int:tier>")
def buy(tier):
    if tier not in PLANS:
        return Response("Plano inexistente", status=404)
    name, amount = PLANS[tier]
    pix = create_pix(amount, f"Estudio do Cantor - Licenca {name}")
    html = (PAGE
            .replace("__PLAN_NAME__", f"Licença {name}")
            .replace("__AMOUNT__", str(amount))
            .replace("__QR64__", pix["qr_base64"])
            .replace("__QR_PAYLOAD__", pix["qr_payload"])
            .replace("__PID__", str(pix["id"])))
    return Response(html, content_type="text/html; charset=utf-8")


@app.get("/status/<pid>")
def status(pid):
    try:
        payment = get_payment(pid)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500
    st = payment.get("status")
    chave = None
    if st == "approved":
        chave = _key_from_ledger(pid)
        if not chave:
            process_payment(payment)
            chave = _key_from_ledger(pid)
    return jsonify(ok=True, status=st, chave=chave)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    try:
        from waitress import serve
        print(f"Servidor de licenças na porta {port} (waitress)")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        print(f"Servidor de licenças na porta {port} (flask dev)")
        app.run(host="0.0.0.0", port=port)
