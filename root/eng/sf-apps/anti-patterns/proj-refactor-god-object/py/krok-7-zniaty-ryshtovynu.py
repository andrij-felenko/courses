class OrderService:                      # ← більше не Manager
    def __init__(self, validator, pricer, repo, notifier):
        self._validator = validator      # усе подано ЗЗОВНІ
        self._pricer = pricer
        self._repo = repo
        self._notifier = notifier

    def place_order(self, cart, user):
        self._validator.check(cart)
        total = self._pricer.total(cart, user)
        self._repo.save(user, total)
        self._notifier.order_placed(user, total)
        return total

# ── композиційний корінь: єдине місце, де програма знає справжні залежності ──
def build_order_service():
    return OrderService(
        OrderValidator(),
        Pricer(),
        OrderRepository(db.connect),
        EmailNotifier(lambda: smtplib.SMTP("mail.local")),
    )
