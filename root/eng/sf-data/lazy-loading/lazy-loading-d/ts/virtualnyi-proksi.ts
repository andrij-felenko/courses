class CustomerProxy implements Customer {
  private real: RealCustomer | null = null;
  constructor(private id: number) {}                   // тримає лише ключ

  private load(): RealCustomer {
    return this.real ??= db.loadCustomer(this.id);     // справжнього створює раз
  }
  get name(): string  { return this.load().name; }     // кожен метод делегує
  get email(): string { return this.load().email; }
}
