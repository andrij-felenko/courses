// стратегія — це просто тип функції
type DiscountPolicy = (order: Order) => number;

const vip: DiscountPolicy        = (o) => o.total * 0.20;
const seasonal = (rate: number): DiscountPolicy => (o) => o.total * rate;

class Order {
  constructor(public total: number, private policy: DiscountPolicy) {}
  finalPrice(): number { return this.total - this.policy(this); }
}

const order = new Order(1000, vip);              // передаємо функцію, не об'єкт
order.finalPrice();                              // 800
new Order(1000, seasonal(0.30)).finalPrice();    // 700
