class OrderService:
    def __init__(self):
        self._gateway = Locator.get("gateway")
        self._clock = Locator.get("clock")
        self._log = Locator.get("audit")
        self._receipts = ReceiptBuilder()

    def checkout(self, order):
        charge_id = self._gateway.charge(order.total())
        receipt = self._receipts.build(order, charge_id)
        self._log.write(f"{self._clock.now()} order={order.id} charge={charge_id}")
        return receipt
