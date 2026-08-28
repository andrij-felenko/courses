// ІЗ фасадом: контролер знає РІВНО ОДИН тип підсистеми — сам фасад
class CheckoutController {
  constructor(private checkout: CheckoutFacade) {}   // єдина залежність

  handlePost(cart: Cart, card: Card): Response {
    const result = this.checkout.placeOrder(cart, card);
    if (result.ok) return Response.ok(result.orderId);
    switch (result.reason) {
      case "out_of_stock": return Response.conflict("Розкупили");
      case "declined":     return Response.paymentRequired("Відхилено");
    }
  }
}
