# Підробка замість мережі: тест ядра БЕЗ Stripe і без інтернету
class FakeGateway(PaymentGateway):
    def __init__(self):
        self.last_amount = None

    def charge(self, amount: Money, card: Card) -> ChargeResult:
        self.last_amount = amount         # просто запам'ятали, що просили
        return ChargeResult(ok=True, reason="")  # і вдали успіх

# PaymentService(fake).charge(order)
# перевіряємо: fake.last_amount == order.total()  — за мілісекунди, без мережі
