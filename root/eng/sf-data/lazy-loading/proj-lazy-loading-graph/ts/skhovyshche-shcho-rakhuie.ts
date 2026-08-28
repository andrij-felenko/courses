type Row = Record<string, any>;

class Db {
  // дві «таблиці» в пам'яті; кожен похід рахуємо
  private customers = new Map<number, Row>([
    [1, { id: 1, name: "Ада",   city: "Лондон" }],
    [2, { id: 2, name: "Грейс", city: "Нью-Йорк" }],
    [3, { id: 3, name: "Лінус", city: "Гельсінкі" }],
  ]);
  private orders = new Map<number, Row>(
    Array.from({ length: 100 }, (_, k): [number, Row] => {
      const i = k + 1;                       // замовлення розкидані на трьох: (i % 3) + 1
      return [i, { id: i, customerId: (i % 3) + 1, total: 10 * i }];
    }),
  );
  queries = 0;                                            // лічильник запитів

  findAllOrders(): Row[] {
    this.queries++;                                       // один SELECT на весь список
    return [...this.orders.values()].map((r) => ({ ...r }));
  }
  findCustomer(id: number): Row {
    this.queries++;                                       // один SELECT на один рядок
    return { ...this.customers.get(id)! };
  }
  findCustomers(ids: number[]): Map<number, Row> {
    this.queries++;                                       // один SELECT ... WHERE id IN (...)
    const want = new Set(ids);
    const out = new Map<number, Row>();
    for (const [id, r] of this.customers) if (want.has(id)) out.set(id, { ...r });
    return out;
  }
  findOrdersJoinCustomer(): Row[] {
    this.queries++;                                       // один SELECT ... JOIN — покупець їде в кожному рядку
    return [...this.orders.values()].map((r) => ({
      ...r,
      customer: { ...this.customers.get(r.customerId)! },
    }));
  }
}
