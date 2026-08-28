# Каркас створює ЦЕЙ клас сам — тут смикнути можна, бо іншого входу нема
class CheckoutController:
    def __init__(self):
        self._core = OrderService(                 # єдиний смик — на самій межі
            Locator.get("gateway"),
            Locator.get("clock"),
            Locator.get("audit"),
            ReceiptBuilder(Locator.get("templates")),
        )

    def handle(self, req):
        return ok(self._core.checkout(to_order(req)))   # уся логіка — у чесному ядрі
