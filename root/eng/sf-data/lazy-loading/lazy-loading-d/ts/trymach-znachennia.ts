class ValueHolder<T> {
  private value: T | null = null;
  constructor(private fetch: () => T) {}                 // як дістати — знає обгортка

  getValue(): T {
    if (this.value === null) this.value = this.fetch();  // перший виклик тягне
    return this.value;
  }
}

class Order {
  readonly customer: ValueHolder<Customer>;
  constructor(readonly id: number, customerId: number) {
    this.customer = new ValueHolder(() => db.loadCustomer(customerId));
  }
}

order.customer.getValue().name;   // клієнт свідомо просить значення
