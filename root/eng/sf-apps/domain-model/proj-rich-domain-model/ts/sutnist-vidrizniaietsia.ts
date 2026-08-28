type Tier = "regular" | "gold";

class Product {                                  // сутність: свій id, свій стан складу
  constructor(
    readonly id: string,
    private readonly unitPrice: Money,
    private _stock: number,
  ) {
    if (_stock < 0) throw new DomainError("залишок не буває від'ємний");
  }
  price(): Money { return this.unitPrice; }
  stock(): number { return this._stock; }
  reserve(qty: number): void {                   // метод-команда: товар сам стереже склад
    if (qty <= 0)            throw new DomainError("резервувати можна лише додатну кількість");
    if (qty > this._stock)   throw new DomainError(`на складі лише ${this._stock}`);
    this._stock -= qty;
  }
}

class Customer {                                 // сутність: свій рівень лояльності
  constructor(readonly id: string, private readonly tier: Tier) {}
  discountPercent(): number { return this.tier === "gold" ? 10 : 0; }  // знає свій відсоток
}

class OrderLine {                                // всередині агрегату замовлення
  constructor(
    readonly productId: string,                  // товар — за id, а не посиланням
    readonly unitPrice: Money,                   // знімок ціни на мить додавання
    readonly qty: number,
  ) {
    if (qty <= 0) throw new DomainError("кількість у позиції має бути додатна");
  }
  subtotal(): Money { return this.unitPrice.times(this.qty); }  // рахує сам, знімком ціни
}
