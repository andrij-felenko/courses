type Status = "draft" | "placed" | "shipped" | "cancelled";

class Order {
  private _status: Status = "draft";
  private readonly _lines: OrderLine[] = [];
  private _total: Money | null = null;                   // підсумку нема, доки не оформлено

  constructor(
    readonly id: string,
    readonly customerId: string,                         // клієнт — за id, а не посиланням
  ) {}

  // ── команди: єдиний спосіб зрушити стан, і в кожній — вартовий ──
  addLine(product: Product, qty: number): void {
    if (this._status !== "draft")
      throw new DomainError("позиції можна додавати лише чернетці");
    product.reserve(qty);                                // розмова з Product: хай стереже склад
    this._lines.push(new OrderLine(product.id, product.price(), qty));
  }

  place(customer: Customer): void {
    if (this._status !== "draft")
      throw new DomainError("оформити можна лише чернетку");
    if (this._lines.length === 0)
      throw new DomainError("порожнє замовлення оформити не можна");

    const sum = this._lines
      .map(line => line.subtotal())                              // OrderLine рахує сам
      .reduce((a, b) => a.add(b), Money.zero(this.currency()));  // Money додає сам
    this._total = sum.withDiscountPercent(customer.discountPercent()); // Customer дає свій відсоток
    this._status = "placed";                             // інваріант циклу — під замком самого Order
  }

  ship(): void {
    if (this._status !== "placed")
      throw new DomainError("відвантажити можна лише оформлене замовлення");
    this._status = "shipped";
  }

  cancel(): void {
    if (this._status !== "draft" && this._status !== "placed")
      throw new DomainError("скасувати можна лише чернетку або оформлене");
    this._status = "cancelled";
  }

  // ── запити ──
  get status(): Status { return this._status; }
  total(): Money {
    if (this._total === null)
      throw new DomainError("підсумок з'являється лише в оформленого замовлення");
    return this._total;
  }
  private currency(): string { return this._lines[0].unitPrice.currency; }
}
