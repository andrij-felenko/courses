class Order {
  discountFor(customer: Customer): number {
    // усі знижкові правила зашиті в один метод
    if (customer.tier === "vip")        return this.total * 0.20;
    if (customer.tier === "loyal")      return this.total * 0.10;
    if (customer.isFirstPurchase)       return this.total * 0.05;
    if (this.isBlackFriday())           return this.total * 0.30;
    return 0;
  }
}
