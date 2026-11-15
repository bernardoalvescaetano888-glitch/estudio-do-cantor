# -*- coding: utf-8 -*-
"""
deliver.py — Processa o pagamento aprovado e entrega a licença:
1. Valor pago -> plano (70=PLUS, 100=MAX, 140=ULTRA)
2. Gera a chave mensal (lic_core)
3. Enva por e-mail ao cliente (se SMTP configurado) e registra em vendas.json
"""
import os
import sys
import json
import smtplib
from email.message import EmailMessage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lic_core as lic                     # noqa: E402
from mp_api import plan_from_amount        # noqa: E402

LEDGER = os.path.join(HERE, "vendas.json")

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")


def send_email(to: str, subject: str, body: str) -> bool:
    if not (EMAIL_USER and EMAIL_PASS and to):
        print(f"  ⚠ SMTP não configurado. Enviar manualmente para {to}")
        return False
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_USER
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(EMAIL_USER, EMAIL_PASS)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"  ⚠ Falha ao enviar e-mail para {to}: {e}")
        return False


def record(sale: dict):
    try:
        ledger = []
        if os.path.exists(LEDGER):
            with open(LEDGER, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        ledger.append(sale)
        with open(LEDGER, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"  ⚠ Erro ao registrar venda: {e}")


def process_payment(payment: dict) -> str:
    status = payment.get("status")
    pid = payment.get("id")
    if status != "approved":
        return f"pagamento {pid} ignorado (status: {status})"

    # Idempotência: pagamento já entregue? reenvia a MESMA chave (evita duplicar)
    if os.path.exists(LEDGER):
        try:
            with open(LEDGER, "r", encoding="utf-8") as f:
                for sale in json.load(f):
                    if str(sale.get("id")) == str(pid) and sale.get("chave"):
                        payer = ((payment.get("payer") or {}).get("email")) or ""
                        resend = send_email(
                            payer, f"🎵 Sua licença {sale['plano']} — Estúdio do Cantor",
                            f"Sua chave (pagamento {pid}):\n\n    {sale['chave']}\n\n"
                            "Abra o app → ⭐ Ativar licença → cole a chave.")
                        return (f"pagamento {pid} já processado — "
                                f"chave reenviada ({resend})")
        except Exception:
            pass

    amount = float(payment.get("transaction_amount", 0) or 0)
    tier = plan_from_amount(amount)
    if not tier:
        msg = f"valor R$ {amount:.2f} não corresponde a nenhum plano (70/100/140)"
        record({"id": pid, "status": "sem_plano", "valor": amount})
        return msg

    payer = ((payment.get("payer") or {}).get("email")) or ""
    key = lic.renew(tier, months=1)
    name = lic.TIER_NAMES[tier]

    body = (
        f"Obrigado pela compra! 🎶\n\n"
        f"Plano: {name} (R$ {amount:.0f}/mês)\n"
        f"Sua chave de licença:\n\n    {key}\n\n"
        f"Como ativar:\n"
        f"1) Abra o Estúdio do Cantor\n"
        f"2) Clique em ⭐ Ativar licença\n"
        f"3) Cole a chave acima e pronto!\n\n"
        f"A chave é válida por 31 dias (renovação automática do Mercado Pago).\n"
    )
    sent = send_email(payer, f"🎵 Sua licença {name} — Estúdio do Cantor", body)
    record({"id": pid, "email": payer, "plano": name, "tier": tier,
            "chave": key, "valor": amount, "email_enviado": sent})
    return f"pagamento {pid}: {name} gerado p/ {payer} (enviado: {sent})"


if __name__ == "__main__":
    # Teste manual: python deliver.py <payment_id>
    from mp_api import get_payment
    if len(sys.argv) != 2:
        print("Uso: python deliver.py <payment_id>")
        sys.exit(1)
    print(process_payment(get_payment(sys.argv[1])))
