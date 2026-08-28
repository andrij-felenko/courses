// Фасад над підсистемою оформлення: складає крихкий порядок в один метод
class CheckoutFacade {
  constructor(
    private inventory: InventoryService,
    private payments: PaymentGateway,
    private orders: OrderRepository,
    private mailer: EmailService,
  ) {}

  placeOrder(cart: Cart, card: Card): OrderId {
    // порядок кроків — крихкий, і він захований ТУТ, а не в клієнті
    this.inventory.reserve(cart.items);          // 1. спершу резерв
    const charge = this.payments.charge(card, cart.total);  // 2. тоді гроші
    const order = this.orders.create(cart, charge.id);       // 3. запис
    this.mailer.sendConfirmation(order);          // 4. і лише тепер лист
    return order.id;
  }
}

// Клієнт (веб-контролер) не знає ні кроків, ні їхнього порядку:
const id = checkout.placeOrder(cart, card);
