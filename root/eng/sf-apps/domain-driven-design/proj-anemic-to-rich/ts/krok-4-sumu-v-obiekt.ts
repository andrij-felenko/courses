// Об'єкт-значення: незмінний, самоперевірний, порівнюється за значенням
class Money {
  private constructor(
    readonly cents: number,        // тримаємо в копійках — жодних дробових гривень
    readonly currency: string,
  ) {}

  static of(amount: number, currency: string): Money {
    if (!Number.isInteger(amount) || amount < 0)
      throw new DomainError("сума має бути невід'ємним цілим числом копійок");
    return new Money(amount, currency);
  }

  static zero(currency: string): Money { return new Money(0, currency); }

  plus(other: Money): Money {
    this.sameCurrency(other);
    return new Money(this.cents + other.cents, this.currency);
  }

  isGreaterThan(other: Money): boolean {
    this.sameCurrency(other);
    return this.cents > other.cents;
  }

  private sameCurrency(other: Money): void {
    if (this.currency !== other.currency)
      throw new DomainError(`не складаються різні валюти: ${this.currency} і ${other.currency}`);
  }
}
