from dataclasses import dataclass, field

@dataclass
class OrderInput:
    product_id: int; qty: int; unit_price: float; stock: int
    discount: float; region: str

class Order:
    def __init__(self, i: OrderInput):
        # інваріанти перевіряються ОДИН раз — у мить народження об'єкта
        if i.qty < 1:
            raise ValueError("кількість має бути ≥ 1")
        if i.stock < i.qty:
            raise ValueError("недостатньо на складі")

        subtotal = i.unit_price * i.qty
        net = subtotal * (1 - i.discount)
        floor = region_floor(i.region)
        # інваріант, що ЗЧІПЛЯЄ поля: чиста сума ніколи не нижча за поріг регіону
        self.discount = (1 - floor / subtotal if subtotal > 0 else 0) if net < floor else i.discount
        net = max(net, floor)
        self.total = net * (1 + region_tax(i.region))
        self.lines = [{"product_id": i.product_id, "qty": i.qty, "price": i.unit_price}]
