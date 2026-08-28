# Та сама база: пачковий метод сам кличе перевизначуваний add.
class Bag:
    def __init__(self):        self.items = []
    def add(self, e):          self.items.append(e)
    def add_all(self, xs):
        for e in xs: self.add(e)                    # ← самовиклик

# Нащадок рахує — і ловить те саме подвоєння.
class CountingBag(Bag):
    def __init__(self):
        super().__init__(); self.count = 0
    def add(self, e):     self.count += 1;      super().add(e)
    def add_all(self, xs): self.count += len(xs); super().add_all(xs)

# CountingBag().add_all(["a","b","c"])  →  count == 6, а не 3
