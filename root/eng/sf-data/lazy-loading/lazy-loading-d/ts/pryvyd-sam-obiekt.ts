class Customer {
  private loaded = false;
  private _name = "";
  private _email = "";
  constructor(readonly id: number) {}          // «привид»: лише id, полів ще нема

  private fill(): void {
    if (this.loaded) return;
    const row = db.loadCustomer(this.id);       // один запит — і ВСІ поля разом
    this._name = row.name;
    this._email = row.email;
    this.loaded = true;
  }
  get name(): string  { this.fill(); return this._name; }
  get email(): string { this.fill(); return this._email; }
}
