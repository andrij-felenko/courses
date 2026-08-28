# infra/smtp_notifier.py ── ЄДИНЕ місце, що знає SMTP. Мапить домен ↔ лист.
from email.message import EmailMessage
from domain.order import Order


class SmtpNotifier:
    def __init__(self, smtp, sender: str):
        self._smtp = smtp
        self._from = sender

    async def order_placed(self, o: Order) -> None:
        msg = EmailMessage()
        msg["From"] = self._from
        msg["To"] = o.email                          # домен дав пошту — SMTP її вживає
        msg["Subject"] = f"Замовлення {o.id} прийнято"
        msg.set_content(f"Дякуємо! Сума до сплати: {o.total()} грн.")
        await self._smtp.send(msg)
