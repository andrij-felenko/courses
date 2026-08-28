# ІЗ фасадом: контролер знає РІВНО ОДИН тип підсистеми — сам фасад
class CheckoutController:
    def __init__(self, checkout: CheckoutFacade):
        self._checkout = checkout        # єдина залежність

    def handle_post(self, cart: Cart, card: Card) -> "Response":
        result = self._checkout.place_order(cart, card)
        if result.ok:
            return Response.ok(result.order_id)
        if result.reason == "out_of_stock":
            return Response.conflict("Розкупили")
        if result.reason == "declined":
            return Response.payment_required("Відхилено")
