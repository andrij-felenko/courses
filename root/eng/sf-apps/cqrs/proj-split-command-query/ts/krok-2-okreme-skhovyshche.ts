// МОДЕЛЬ ЧИТАННЯ: денормалізований знімок, усе для картки в одному рядку.
type OrderReadModel = {
  id: string;
  userId: string;
  customerName: string;   // ← уже склеєно, жодного JOIN на читанні
  total: number;
  status: string;
  updatedAt: number;      // коли знімок востаннє наздогнав запис
};

class OrderReadStore {
  constructor(private kv: KeyValueDb) {}          // окреме сховище під читання

  byId(id: string): OrderReadModel | null {
    return this.kv.get(`order:${id}`);            // один доторок за ключем
  }
  listByUser(userId: string): OrderReadModel[] {
    return this.kv.getByIndex("order_by_user", userId); // готовий індекс
  }

  // сюди пише ЛИШЕ проєкція (крок 3), не бізнес-код
  upsert(m: OrderReadModel): void {
    this.kv.put(`order:${m.id}`, m);
    this.kv.index("order_by_user", m.userId, m.id);
  }
}
