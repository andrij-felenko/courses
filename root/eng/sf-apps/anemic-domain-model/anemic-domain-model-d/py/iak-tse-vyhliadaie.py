# Знекровлена модель: замовлення нічого не вміє, лише тримає поля навстіж
class Order:
    def __init__(self):
        self.status = "new"       # "new" | "paid" | "shipped" | "cancelled"
        self.items = []
        self.discount = 0         # відсоток знижки, 0..100 — ніхто не стереже
        self.total = 0

# Уся думка — ЗЗОВНІ, у сервісі; кожен викликач тримає свій уламок правил
class OrderService:
    def apply_discount(self, o, percent):
        o.discount = percent      # жодної перевірки: приймуться й 500, і −20
        o.total = sum(i.price for i in o.items) * (1 - o.discount / 100)

    def ship(self, o):
        # тут ЗАБУЛИ перевірити, що замовлення взагалі оплачене
        o.status = "shipped"
