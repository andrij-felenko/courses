class Order {
  private _customer: Customer | null = null;      // ще не тягнули
  constructor(readonly id: number, private customerId: number) {}

  get customer(): Customer {
    if (this._customer === null) {
      this._customer = db.loadCustomer(this.customerId);   // один похід у базу
    }
    return this._customer;
  }
}
