class Billing {
  constructor(private readonly feeRate: number) {}   // залежність на видноті

  charge(order: Order): number {
    return order.total * this.feeRate;
  }
}

// тест тривіальний і повністю ізольований:
expect(new Billing(0.02).charge(order)).toBe(expected);
