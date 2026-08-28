type OrderId = string;
type CustomerId = string;
type OrderStatus = "new" | "paid" | "shipped";

class Order {
  private _status: OrderStatus;

  constructor(
    readonly id: OrderId,
    readonly customerId: CustomerId,
    readonly total: number,
    readonly createdAt: Date,
    status: OrderStatus = "new",
  ) {
    this._status = status;
  }

  get status(): OrderStatus { return this._status; }
  isPaid(): boolean { return this._status === "paid"; }

  markPaid(): void {
    if (this._status !== "new") {
      throw new Error(`оплатити можна лише нове замовлення, а це «${this._status}»`);
    }
    this._status = "paid";
  }
}
