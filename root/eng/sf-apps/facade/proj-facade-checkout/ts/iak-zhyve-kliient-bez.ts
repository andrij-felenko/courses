// БЕЗ фасаду: контролер сам знає всі 4 служби, порядок і відкіт
class CheckoutController {
  constructor(
    private inventory: InventoryService,   // залежність 1
    private payments: PaymentGateway,      // залежність 2
    private orders: OrderRepository,       // залежність 3
    private mailer: EmailService,          // залежність 4
  ) {}

  handlePost(cart: Cart, card: Card): Response {
    let reservation: ReservationId | null = null;
    try {
      reservation = this.inventory.reserve(cart.items);          // крок 1
      const charge = this.payments.charge(card, cart.total);     // крок 2
      const order  = this.orders.create(cart, charge.id);        // крок 3
      try { this.mailer.sendConfirmation(order); }               // крок 4
      catch { /* лист не критичний — ковтаємо */ }
      return Response.ok(order.id);
    } catch (e) {
      if (reservation) this.inventory.release(reservation);      // відкіт!
      if (e instanceof OutOfStockError)      return Response.conflict("Розкупили");
      if (e instanceof PaymentDeclinedError) return Response.paymentRequired("Відхилено");
      throw e;
    }
  }
}
