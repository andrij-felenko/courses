class ReceiptBuilder:
    def build(self, order, charge_id):
        templates = Locator.get("templates")          # смик усередині дитини
        return templates.render("receipt", order=order.id, charge=charge_id)


class OrderService:
    def checkout(self, order):
        gateway = Locator.get("gateway")              # смик 1
        clock = Locator.get("clock")                  # смик 2
        charge_id = gateway.charge(order.total())
        receipt = ReceiptBuilder().build(order, charge_id)
        self._audit(order, charge_id, clock)
        return receipt

    def _audit(self, order, charge_id, clock):
        log = Locator.get("audit")                    # смик 3, у надрах
        log.write(f"{clock.now()} order={order.id} charge={charge_id}")
