// Внутрішня частина агрегату — теж незмінна, живе лише всередині поліса
class Payment {
  constructor(readonly amount: Money, readonly at: Date) {}
}

class Policy {                       // ← корінь агрегату
  private _payments: Payment[] = []; // внутрішня частина — закрита
  /* ...стан, премія, переходи — як раніше... */

  // єдині двері: платіж додають ЛИШЕ через корінь, і тут тримається інваріант
  addPayment(amount: Money, at: Date): void {
    if (this._status !== PolicyStatus.Active && this._status !== PolicyStatus.Grace)
      throw new DomainError("платіж приймають лише за чинним полісом");
    // рахуємо суму ДО додавання — і ту саму величину перевіряємо
    const afterPay = this.paidTotal().plus(amount);  // кине, якщо валюти різні
    if (afterPay.isGreaterThan(this._premium))
      throw new DomainError("сума платежів не може перевищити премію");
    this._payments.push(new Payment(amount, at));    // інваріант ≤ премія тут тримається
  }

  paidTotal(): Money {
    return this._payments.reduce((s, p) => s.plus(p.amount),
                                 Money.zero(this._premium.currency));
  }

  // назовні — незмінний знімок, а не жива внутрішня колекція
  get payments(): readonly Payment[] { return [...this._payments]; }
}
