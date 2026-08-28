type PlaceOrder = { customerId: string; items: LineItem[] };

class OrderService {
  constructor(private db: Db) {}   // приватна база сервісу замовлень

  async placeOrder(cmd: PlaceOrder): Promise<string> {
    const order = Order.create(cmd.customerId, cmd.items);

    // ── ОДНА локальна транзакція: замовлення + намір сповістити склад ──
    await this.db.transaction(async (tx) => {
      await tx.insert("orders", {
        id: order.id,
        customer_id: order.customerId,
        status: "placed",
        total: order.total,
      });

      // рядок OUTBOX — намір, що поїде в чергу окремим реле.
      // eventId генеруємо ТУТ і кладемо в тіло — саме за ним споживач
      // упізнаватиме дублі. topic каже реле, у яку чергу це слати.
      await tx.insert("outbox", {
        event_id: crypto.randomUUID(),
        topic: "OrderPlaced",
        payload: JSON.stringify({ orderId: order.id, items: order.items }),
        sent: false,
        created_at: new Date(),
      });
    }); // ← коміт: або лягли ОБИДВА рядки, або жоден. Подвійного запису немає.

    return order.id;
  }
}
