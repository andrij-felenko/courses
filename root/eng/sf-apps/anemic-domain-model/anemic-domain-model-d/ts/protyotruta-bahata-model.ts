class Order {
  private _status = "new";
  private _discount = 0;
  private _items: Item[] = [];

  // правило знижки тепер ТУТ, разом зі своїм вартовим
  applyDiscount(percent: number): void {
    if (this._status !== "new")
      throw new DomainError("знижку міняють лише до оплати");
    if (percent < 0 || percent > 100)
      throw new DomainError("знижка поза межами 0..100");
    this._discount = percent;
  }

  ship(): void {
    if (this._status !== "paid")           // перевірка, якої бракувало
      throw new DomainError("відвантажують лише оплачене");
    this._status = "shipped";
  }
}
