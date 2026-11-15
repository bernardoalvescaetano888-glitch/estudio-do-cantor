# -*- coding: utf-8 -*-
"""
mp_api.py — Cliente da API do Mercado Pago
Base: https://api.mercadopago.com  (autenticação: Bearer token no header)
"""
import os
import requests

BASE = "https://api.mercadopago.com"

# Preços dos planos -> tier
PRICE_TIERS = {70: 1, 100: 2, 140: 3}


def token() -> str:
    return os.environ.get("MP_ACCESS_TOKEN", "").strip()


def headers() -> dict:
    t = token()
    if not t:
        raise RuntimeError("MP_ACCESS_TOKEN não configurado (.env ou variável de ambiente).")
    return {"Authorization": f"Bearer {t}", "Content-Type": "application/json"}


def get_payment(payment_id):
    """GET /v1/payments/{id} — status, valor, e-mail do pagador."""
    r = requests.get(f"{BASE}/v1/payments/{payment_id}", headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def create_payment_link(title: str, price: int, webhook_url: str = None) -> str:
    """POST /checkout/preferences — cria link de pagamento (Checkout Pro)."""
    body = {
        "items": [{"title": title, "quantity": 1, "unit_price": float(price),
                   "currency_id": "BRL"}],
    }
    if webhook_url:
        body["notification_url"] = webhook_url
    r = requests.post(f"{BASE}/checkout/preferences", headers=headers(),
                      json=body, timeout=30)
    r.raise_for_status()
    return r.json()["init_point"]


def plan_from_amount(amount: float, tolerance: float = 5.0):
    """Mapeia o valor pago para o tier do plano (tolerância p/ arredondamentos)."""
    for price, tier in PRICE_TIERS.items():
        if abs(amount - price) <= tolerance:
            return tier
    return None
