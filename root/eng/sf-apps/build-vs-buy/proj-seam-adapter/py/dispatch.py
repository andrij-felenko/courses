# domain/dispatch.py — ЯДРО. Знає лише порт Notifier.
class OrderDispatch:
    def __init__(self, notifier: Notifier) -> None:    # впровадження залежності
        self._notifier = notifier

    def on_courier_assigned(self, order: Order, customer: Recipient) -> None:
        outcome = self._notifier.notify(
            customer, CourierNear(order_id=order.id, minutes_away=order.eta_minutes)
        )
        # рішення домену — без знання про 429 чи 421
        if outcome.status == "retryable":
            self._schedule_retry(order)

# main.py — КОМПОЗИЦІЙНИЙ КОРІНЬ: єдине місце вибору постачальника.
def build_notifier() -> Notifier:
    if os.environ.get("MAIL") == "smtp":
        return SmtpNotifier("mail.example.com", 587, "no-reply@food.app")
    return SendGridNotifier(os.environ["SENDGRID_KEY"], "no-reply@food.app")

dispatch = OrderDispatch(build_notifier())     # ядро дістає порт, не знаючи, який адаптер
