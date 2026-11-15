# -*- coding: utf-8 -*-
"""
mp_links.py — Cria os 3 links de pagamento (PLUS/MAX/ULTRA) via API do MP
e já conecta o webhook para entrega automática.

Uso:
    python mp_links.py            # cria links com os preços padrão (70/100/140)
    python mp_links.py --webhook https://seu-server.onrender.com/webhook
"""
import os
import sys
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))
sys.path.insert(0, HERE)

from mp_api import create_payment_link   # noqa: E402

PLANS = [
    ("Estúdio do Cantor — Licença PLUS (R$ 70/mês)", 70),
    ("Estúdio do Cantor — Licença MAX (R$ 100/mês)", 100),
    ("Estúdio do Cantor — Licença ULTRA (R$ 140/mês)", 140),
]


def main():
    webhook = sys.argv[sys.argv.index("--webhook") + 1] if "--webhook" in sys.argv \
        else os.environ.get("WEBHOOK_URL", "")
    if not webhook:
        print("⚠ Sem webhook: as vendas virarão apenas notificação de e-mail no MP.\n"
              "  Informe com --webhook https://seu-servidor/webhook para automação total.\n")

    print("=== LINKS DE PAGAMENTO MERCADO PAGO ===\n")
    for title, price in PLANS:
        url = create_payment_link(title, price, webhook or None)
        tier = {70: "PLUS", 100: "MAX", 140: "ULTRA"}[price]
        print(f"  {tier:5} R$ {price:>3}/mês  ->  {url}\n")
    print("Coloque o link do plano na bio/Instagram e no STORE_URL do app.py.")


if __name__ == "__main__":
    main()
