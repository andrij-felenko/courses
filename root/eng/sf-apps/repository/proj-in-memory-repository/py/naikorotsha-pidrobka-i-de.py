class PaymentService:
    def __init__(self, orders: OrderRepository, gateway: PaymentGateway) -> None:
        self._orders, self._gateway = orders, gateway

    def pay(self, order_id: OrderId) -> None:
        order = self._orders.by_id(order_id)
        if order is None:
            raise LookupError(f"немає замовлення {order_id}")
        self._gateway.charge(order.total)
        order.mark_paid()
        # ← і тут забули: self._orders.save(order)
