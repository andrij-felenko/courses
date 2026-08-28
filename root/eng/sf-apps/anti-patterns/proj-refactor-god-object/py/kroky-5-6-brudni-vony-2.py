class OrderManager:
    def __init__(self):
        self._validator = OrderValidator()                     # ← сам
        self._pricer = Pricer()                                # ← сам
        self._repo = OrderRepository(self._open_db)            # ← сам
        self._notifier = EmailNotifier(self._open_smtp)        # ← сам

    def place_order(self, cart, user):
        self._validator.check(cart)
        total = self._pricer.total(cart, user)
        self._repo.save(user, total)
        self._notifier.order_placed(user, total)
        return total

    def _open_db(self):   return db.connect()
    def _open_smtp(self): return smtplib.SMTP("mail.local")
