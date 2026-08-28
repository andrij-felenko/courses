class ReceiptBuilder:
    def __init__(self, templates=None):
        # сентинел None, а НЕ typedefault=Locator.get(...) — чому, див. нижче
        self._templates = templates if templates is not None else Locator.get("templates")

    def build(self, order, charge_id):
        return self._templates.render("receipt", order=order.id, charge=charge_id)


class OrderService:
    def __init__(self, gateway=None, clock=None, log=None, receipts=None):
        self._gateway = gateway if gateway is not None else Locator.get("gateway")
        self._clock = clock if clock is not None else Locator.get("clock")
        self._log = log if log is not None else Locator.get("audit")
        self._receipts = receipts if receipts is not None else ReceiptBuilder()

    def checkout(self, order):
        charge_id = self._gateway.charge(order.total())
        receipt = self._receipts.build(order, charge_id)
        self._log.write(f"{self._clock.now()} order={order.id} charge={charge_id}")
        return receipt
