// Фасад: тримає підсистему, порядок і відкіт. Клієнт не знає нічого з цього.
class CheckoutFacade {
  constructor(
    private inventory: InventoryService,
    private payments: PaymentGateway,
    private orders: OrderRepository,
    private mailer: EmailService,
  ) {}

  placeOrder(cart: Cart, card: Card): OrderResult {
    // Крок 1: резерв. Якщо тут упало — відкочувати ще нічого, просто виходимо.
    let reservation: ReservationId;
    try {
      reservation = this.inventory.reserve(cart.items);
    } catch (e) {
      if (e instanceof OutOfStockError) return { ok: false, reason: "out_of_stock" };
      throw e;
    }

    // Крок 2: платіж. Якщо ВІН упав — резерв уже висить: ЗНІМАЄМО його (компенсація).
    let charge: Charge;
    try {
      charge = this.payments.charge(card, cart.total);
    } catch (e) {
      this.inventory.release(reservation);            // ← відкіт кроку 1
      if (e instanceof PaymentDeclinedError) return { ok: false, reason: "declined" };
      throw e;
    }

    // Крок 3: запис замовлення. Якщо впав — треба зняти І резерв, І платіж.
    let order: Order;
    try {
      order = this.orders.create(cart, charge.id);
    } catch (e) {
      this.payments.refund(charge.id);                // ← відкіт кроку 2
      this.inventory.release(reservation);            // ← відкіт кроку 1
      throw e;                                         // це вже наша вина, не клієнтова
    }

    // Крок 4: лист. НЕ критичний — його збій не валить замовлення й не відкочує.
    try { this.mailer.sendConfirmation(order); }
    catch { /* залогувати й забути: гроші взято, товар зарезервовано, запис є */ }

    return { ok: true, orderId: order.id };
  }
}

type OrderResult =
  | { ok: true;  orderId: string }
  | { ok: false; reason: "out_of_stock" | "declined" };
