# -*- coding: utf-8 -*-
"""
mp_server.py — Servidor de entrega automática de licenças (Mercado Pago)

Fluxo: cliente paga -> MP chama POST /webhook -> buscamos o pagamento na API
-> geramos a chave -> enviamos por e-mail -> registramos em vendas.json

Executar:  python mp_server.py        (produção, via waitress)
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from flask import Flask, request, jsonify   # noqa: E402
from mp_api import get_payment              # noqa: E402
from deliver import process_payment         # noqa: E402

app = Flask(__name__)


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    try:
        from waitress import serve
        print(f"Servidor de licenças na porta {port} (waitress)")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        print(f"Servidor de licenças na porta {port} (flask dev)")
        app.run(host="0.0.0.0", port=port)
