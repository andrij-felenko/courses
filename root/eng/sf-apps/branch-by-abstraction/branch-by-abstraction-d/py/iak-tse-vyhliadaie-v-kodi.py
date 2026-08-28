from abc import ABC, abstractmethod

# Шов: обіцянка мовою клієнта, без натяку на пошту чи чергу
class Notifier(ABC):
    @abstractmethod
    def notify(self, to: str, message: str) -> None: ...

# Стара реалізація тепер лише виконує обіцянку
class LegacyMailerNotifier(Notifier):
    def __init__(self):
        self._mailer = LegacyMailer()
    def notify(self, to, message):
        self._mailer.send_mail(to, message)

class OrderService:
    def __init__(self, notifier: Notifier):    # залежність від шва, не від деталі
        self._notifier = notifier
    def place_order(self, order):
        # ...бізнес-логіка...
        self._notifier.notify(order.email, "Замовлення прийнято")
