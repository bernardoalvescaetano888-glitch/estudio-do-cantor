# -*- coding: utf-8 -*-
"""
pix.py — Gera Pix dinâmico (QR Code + copia-e-cola) via API do Mercado Pago

POST /v1/payments com payment_method_id="pix" devolve:
  - qr_code       → payload copia-e-cola
  - qr_code_base64→ imagem PNG em base64 (pronta pra mostrar na página)

Uso manual: python pix.py 70     → imprime payload e salva qr.png
"""
import os
import sys
import base64
import requests

from mp_api import BASE, headers

PLANS = {1: ("PLUS", 70), 2: ("MAX", 100), 3: ("ULTRA", 140)}


def create_pix(amount: float, description: str, payer_email: str = None) -> dict:
    body = {
        "transaction_amount": round(float(amount), 2),
        "description": description,
        "payment_method_id": "pix",
        "payer": {"email": payer_email} if payer_email
                 else {"email": "comprador@estudiodocantor.app"},
    }
    r = requests.post(f"{BASE}/v1/payments", headers=headers(), json=body, timeout=30)
    r.raise_for_status()
    p = r.json()
    poi = (p.get("point_of_interaction") or {}).get("transaction_data") or {}
    return {
        "id": p.get("id"),
        "status": p.get("status"),
        "valor": amount,
        "qr_payload": poi.get("qr_code", ""),
        "qr_base64": poi.get("qr_code_base64", ""),
    }


def save_qr(pix: dict, path: str = "qr.png"):
    if pix.get("qr_base64"):
        with open(path, "wb") as f:
            f.write(base64.b64decode(pix["qr_base64"]))
        return path
    return None


if __name__ == "__main__":
    tier = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    name, amount = PLANS[tier]
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    pix = create_pix(amount, f"Estudio do Cantor - Licenca {name}")
    print(f"Plano: {name}  |  Valor: R$ {amount}  |  ID pagamento: {pix['id']}")
    print("\nCOPIA E COLA (código Pix):\n")
    print(pix["qr_payload"])
    png = save_qr(pix)
    if png:
        print(f"\nQR salvo em: {os.path.abspath(png)}")
