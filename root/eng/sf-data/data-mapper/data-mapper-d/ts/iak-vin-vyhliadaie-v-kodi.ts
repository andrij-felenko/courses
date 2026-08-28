// ── ДОМЕН: жодного натяку на базу ──────────────────────────────
class Money {
  constructor(readonly cents: number, readonly currency: string) {}
  plus(o: Money): Money {
    if (o.currency !== this.currency) throw new Error("різні валюти не додаються");
    return new Money(this.cents + o.cents, this.currency);
  }
  times(k: number): Money { return new Money(Math.round(this.cents * k), this.currency); }
}

class OrderLine {
  constructor(readonly sku: string, readonly qty: number, readonly price: Money) {}
  subtotal(): Money { return this.price.times(this.qty); }
}

type Status = "new" | "shipped" | "cancelled";

class Order {
  constructor(
    readonly id: number | null,
    readonly placedAt: Date,
    readonly lines: readonly OrderLine[],
    private status: Status = "new",
  ) {
    if (lines.length === 0) throw new Error("замовлення без позицій не буває");
  }

  get state(): Status { return this.status; }

  total(): Money {
    return this.lines.slice(1).reduce((s, l) => s.plus(l.subtotal()), this.lines[0].subtotal());
  }

  cancel(): void {
    if (this.status === "shipped") throw new Error("відвантажене не скасовують");
    this.status = "cancelled";
  }
}
