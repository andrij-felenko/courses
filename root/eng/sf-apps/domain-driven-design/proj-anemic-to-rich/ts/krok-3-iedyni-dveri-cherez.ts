class Policy {
  private _status = PolicyStatus.Draft;
  private _premium = 0;
  private _payments: number[] = [];
  /* ...конструктор і переходи стану, як у кроці 2... */

  // ЄДИНІ ДВЕРІ для платежу: сюди зайти можна лише правильним значенням
  addPayment(amount: number): void {
    if (this._status !== PolicyStatus.Active && this._status !== PolicyStatus.Grace)
      throw new DomainError("платіж приймають лише за чинним полісом");
    if (amount <= 0)
      throw new DomainError("платіж має бути додатним");
    if (this.paidTotal() + amount > this._premium)
      throw new DomainError("сума платежів не може перевищити премію");
    this._payments.push(amount);
  }

  paidTotal(): number {
    return this._payments.reduce((s, x) => s + x, 0);
  }

  // назовні — КОПІЯ, а не сам масив: читач не дотягнеться до нутрощів
  get payments(): readonly number[] {
    return [...this._payments];
  }
}
