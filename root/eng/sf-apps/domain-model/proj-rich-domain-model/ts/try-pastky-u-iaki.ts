// ЗАПАХ анемії: об'єкт лише віддає поля, а рахує й вирішує хтось інший
class Order { lines: OrderLine[] = []; status = "draft"; }         // самі дані, жодного правила

class OrderService {
  place(order: Order, customer: Customer) {
    if (order.lines.length === 0) throw new Error("порожнє");      // інваріант утік сюди
    order.status = "placed";                                       // і перехід стану — теж
    // ...і підсумок сервіс рахує сам, лізучи в order.lines
  }
}
