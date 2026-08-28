// ✅ Правильно: дані замовлення — у контексті, стан лишається спільним і чистим
class Order {
  private state: OrderState = States.New;
  paidAt?: Date;                       // ← поле замовлення, не стану
  /* ... */
}
class PaidState extends OrderState {
  readonly name = "Paid";
  ship(order: Order) {
    order.paidAt ??= new Date();       // ← пишемо в КОНКРЕТНЕ замовлення
    order.transitionTo(States.Shipped);
  }
}
