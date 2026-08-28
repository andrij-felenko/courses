# ПІСЛЯ: кожен виконавець робить одне діло; сервіс тільки диригує.
class OrderValidator:
    def check(self, cart): ...          # лише перевірка
class Pricer:
    def total(self, cart, user): ...    # лише ціна
class OrderRepository:
    def save(self, user, total): ...    # лише запис
class Notifier:
    def order_placed(self, user, total): ...  # лише сповіщення

class OrderService:
    def __init__(self, validator, pricer, repo, notifier):
        self._validator = validator      # залежності подано ЗЗОВНІ
        self._pricer = pricer
        self._repo = repo
        self._notifier = notifier

    def place_order(self, cart, user):
        self._validator.check(cart)
        total = self._pricer.total(cart, user)
        self._repo.save(user, total)
        self._notifier.order_placed(user, total)
        return total
