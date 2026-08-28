class Order {
  private _status: Status = "new";
  private _lines: OrderLine[] = [];

  // операція — це розмова, а не процедура: Order нічого не рахує сам,
  // він лише збирає відповіді від тих, хто володіє потрібними даними
  place(customer: Customer): void {
    if (this._lines.length === 0)
      throw new DomainError("порожнє замовлення оформити не можна");
    for (const line of this._lines)
      line.product.reserve(line.qty);        // товар сам стереже свій залишок
    const tier = customer.tier();            // клієнт сам знає свій рівень
    this._total = this._lines
      .map(l => l.subtotal().withDiscount(tier))   // рядок сам рахує свій підсумок
      .reduce((a, b) => a.add(b), Money.zero());    // гроші самі знають, як додаватись
    this._status = "placed";                 // інваріант циклу — під замком самого Order
  }
}
