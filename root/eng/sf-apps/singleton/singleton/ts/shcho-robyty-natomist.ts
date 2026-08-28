// НЕ так: сервіс сам лізе по глобальний конфіг
class OrderService {
  placeOrder(order: Order) {
    const cfg = Config.getInstance();          // прихована залежність
    // ...
  }
}

// А так: залежність приходить явно через конструктор
class OrderService {
  constructor(private cfg: Config) {}          // видно в сигнатурі
  placeOrder(order: Order) {
    // користуємось this.cfg — його дав той, хто складав програму
  }
}
