interface OrderState {
  pay(order: Order): void;
  ship(order: Order): void;
}

class NewState implements OrderState {
  pay(order: Order) {
    // ...провести оплату...
    order.setState(new PaidState());   // стан САМ переводить власника далі
  }
  ship(order: Order) {
    throw new Error("спершу оплатіть");  // у цьому стані відправляти не можна
  }
}

class PaidState implements OrderState {
  pay(order: Order)  { throw new Error("уже оплачено"); }
  ship(order: Order) {
    // ...відвантажити...
    order.setState(new ShippedState());
  }
}

class ShippedState implements OrderState {
  pay(order: Order)  { throw new Error("надто пізно"); }
  ship(order: Order) { throw new Error("уже відправлено"); }
}
