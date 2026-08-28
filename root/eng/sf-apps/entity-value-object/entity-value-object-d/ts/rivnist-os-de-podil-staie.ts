// Об'єкт-значення: рівність — за ВМІСТОМ, тотожності немає.
// Незмінний (readonly), нове значення — новий об'єкт.
class Money {
  constructor(
    readonly amount: number,   // у копійках, щоб не було дробів
    readonly currency: string,
  ) {}

  equals(other: Money): boolean {
    // жодного id — порівнюємо всі атрибути
    return this.amount === other.amount
        && this.currency === other.currency;
  }

  add(other: Money): Money {
    if (this.currency !== other.currency)
      throw new Error("не можна додавати різні валюти");
    return new Money(this.amount + other.amount, this.currency);  // НОВИЙ об'єкт
  }
}

const a = new Money(30000, "UAH");
const b = new Money(30000, "UAH");
a.equals(b);           // true — 300 грн це 300 грн, хоч це різні об'єкти в пам'яті
a === b;               // false — але це вже питання про пам'ять, а не про гроші
