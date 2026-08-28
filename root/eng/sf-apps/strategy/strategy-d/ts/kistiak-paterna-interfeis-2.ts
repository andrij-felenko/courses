class Order {
  constructor(
    public total: number,
    private policy: DiscountPolicy,              // контекст тримає СТРАТЕГІЮ полем
  ) {}

  finalPrice(): number {
    return this.total - this.policy.discount(this); // делегує, не знаючи, яка саме
  }

  setPolicy(policy: DiscountPolicy): void {      // стратегію можна підмінити на льоту
    this.policy = policy;
  }
}

// збірка: хто саме — вирішується ЗЗОВНІ, в одному місці
const order = new Order(1000, new VipDiscount());
order.finalPrice();                              // 800
order.setPolicy(new SeasonalDiscount(0.30));
order.finalPrice();                              // 700
