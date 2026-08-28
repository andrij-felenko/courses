class Entity:
    def __init__(self):
        self.id = None                      # призначить база на INSERT

class Customer(Entity):
    def __init__(self, name, points=0):
        super().__init__()
        self.name, self.points = name, points

class Order(Entity):
    def __init__(self, customer):
        super().__init__()
        self.customer = customer            # посилання на батька
        self.total = 0
