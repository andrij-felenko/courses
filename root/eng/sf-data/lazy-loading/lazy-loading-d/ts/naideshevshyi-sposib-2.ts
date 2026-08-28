private _customer: Customer | null = null;
private loaded = false;

get customer(): Customer | null {
  if (!this.loaded) {
    this._customer = db.loadCustomer(this.customerId);
    this.loaded = true;
  }
  return this._customer;   // тепер null означає «покупця немає», а не «не вантажив»
}
