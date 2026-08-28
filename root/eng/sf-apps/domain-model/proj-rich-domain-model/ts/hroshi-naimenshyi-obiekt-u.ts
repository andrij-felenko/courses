class DomainError extends Error {}

class Money {
  private constructor(
    readonly cents: number,            // копійки цілим числом, не дріб
    readonly currency: string,
  ) {}

  // єдині двері всередину — з вартовим: гроші не бувають від'ємні
  static of(cents: number, currency: string): Money {
    if (!Number.isInteger(cents)) throw new DomainError("копійки мусять бути цілим числом");
    if (cents < 0) throw new DomainError(`гроші не бувають від'ємні: ${cents}`);
    return new Money(cents, currency);
  }
  static zero(currency: string): Money { return new Money(0, currency); }

  add(o: Money): Money {
    this.requireSameCurrency(o);
    return new Money(this.cents + o.cents, this.currency);  // новий об'єкт, старі не змінені
  }
  times(qty: number): Money {
    if (!Number.isInteger(qty) || qty < 0) throw new DomainError("кількість — ціле невід'ємне");
    return new Money(this.cents * qty, this.currency);
  }
  withDiscountPercent(pct: number): Money {
    if (pct < 0 || pct > 100) throw new DomainError("відсоток поза межами 0..100");
    return new Money(this.cents - Math.trunc(this.cents * pct / 100), this.currency);
  }

  equals(o: Money): boolean {              // рівність за ВМІСТОМ — руками, бо оператора нема
    return this.cents === o.cents && this.currency === o.currency;
  }
  private requireSameCurrency(o: Money): void {
    if (this.currency !== o.currency) throw new DomainError("не можна складати різні валюти");
  }
}
