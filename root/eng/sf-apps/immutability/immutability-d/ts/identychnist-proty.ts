class Money {
  constructor(
    readonly amount: number,
    readonly currency: string,
  ) {}

  equals(o: Money): boolean {                 // рівність за ВМІСТОМ, не за посиланням
    return this.amount === o.amount && this.currency === o.currency;
  }

  add(o: Money): Money {                       // «зміна» = новий об'єкт
    if (o.currency !== this.currency) throw new Error("різні валюти");
    return new Money(this.amount + o.amount, this.currency);
  }
}

const a = new Money(100, "UAH");
const b = new Money(100, "UAH");
a === b;        // false — різні примірники (ідентичність)
a.equals(b);    // true  — рівні за значенням
