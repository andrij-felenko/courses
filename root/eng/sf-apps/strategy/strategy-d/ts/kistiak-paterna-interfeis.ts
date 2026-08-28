interface DiscountPolicy {                       // інтерфейс стратегії: одна операція
  discount(order: Order): number;
}

class NoDiscount implements DiscountPolicy {
  discount(order: Order): number { return 0; }
}
class VipDiscount implements DiscountPolicy {
  discount(order: Order): number { return order.total * 0.20; }
}
class SeasonalDiscount implements DiscountPolicy {
  constructor(private rate: number) {}           // стратегія може мати власний стан
  discount(order: Order): number { return order.total * this.rate; }
}
