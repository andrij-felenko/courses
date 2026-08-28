class Policy {
  private _premium: Money;
  private _payments: Money[] = [];
  /* ...інше, як раніше... */

  constructor(id: string, dueDate: Date, premium: Money) {
    this._id = id;
    this._dueDate = dueDate;
    this._premium = premium;         // валюта поліса задана раз, тут
  }

  addPayment(amount: Money): void {
    if (this._status !== PolicyStatus.Active && this._status !== PolicyStatus.Grace)
      throw new DomainError("платіж приймають лише за чинним полісом");
    // «додатність» і «та сама валюта» вже гарантує сам Money — тут не дублюємо
    const afterPay = this.paidTotal().plus(amount);      // кине, якщо валюти різні
    if (afterPay.isGreaterThan(this._premium))
      throw new DomainError("сума платежів не може перевищити премію");
    this._payments.push(amount);
  }

  paidTotal(): Money {
    return this._payments.reduce((s, m) => s.plus(m), Money.zero(this._premium.currency));
  }
}
