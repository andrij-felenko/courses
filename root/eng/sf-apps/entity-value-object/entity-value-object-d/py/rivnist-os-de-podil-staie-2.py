class Order:
    def __init__(self, id: str):
        self.id = id                     # незмінна нитка тотожності
        self.status = "новий"            # стан — мінливий

    def pay(self):    self.status = "оплачений"     # МІНЯЄМО стан — це нормально
    def cancel(self): self.status = "скасований"

    def __eq__(self, other):
        return isinstance(other, Order) and self.id == other.id   # тільки id

    def __hash__(self):
        return hash(self.id)             # хеш теж від id, не від стану

o1 = Order("ord-42")
o1.pay()                                 # стан змінився
same = Order("ord-42")                   # той самий id
o1 == same                               # True — рівність за тотожністю
