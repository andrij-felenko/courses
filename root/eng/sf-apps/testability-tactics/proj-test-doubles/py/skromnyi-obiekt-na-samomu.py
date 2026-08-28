class ConfirmationComposer:
    def compose(self, email: str, total: Money) -> dict[str, str]:
        hrn = f"{total / 100:.2f}"
        return {"to": email, "subject": "Замовлення прийнято",
                "body": f"Дякуємо! До сплати: {hrn} грн."}

class SmtpNotifier:
    def __init__(self, composer: ConfirmationComposer, smtp: "SmtpClient") -> None:
        self._composer = composer      # чиста логіка
        self._smtp = smtp              # чуже, за ВЛАСНИМ портом

    def send_confirmation(self, email: str, total: Money) -> None:
        self._smtp.send(self._composer.compose(email, total))
