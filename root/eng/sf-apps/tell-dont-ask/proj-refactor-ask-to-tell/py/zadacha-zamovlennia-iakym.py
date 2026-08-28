class Order:
    """Замовлення — лише мішок даних: статус назовні, жодного правила всередині."""
    def __init__(self, order_id):
        self.order_id = order_id
        self.status = "new"          # "new" | "paid" | "shipped" | "cancelled"

    def get_status(self):
        return self.status

    def set_status(self, s):
        self.status = s


# --- переходи живуть ЗЗОВНІ, у різних кутках коду ---

# оформлення (шар оплати)
def pay_order(order):
    if order.get_status() == "new":
        order.set_status("paid")
    else:
        raise RuntimeError(f"не можна оплатити: {order.get_status()}")

# склад (інший шар, часто інший автор)
def ship_order(order):
    # тут ЗАБУЛИ перевірити, що замовлення оплачене
    order.set_status("shipped")

# скасування (ще один шар)
def cancel_order(order):
    if order.get_status() != "shipped":
        order.set_status("cancelled")
    else:
        raise RuntimeError("відвантажене вже не скасувати")
