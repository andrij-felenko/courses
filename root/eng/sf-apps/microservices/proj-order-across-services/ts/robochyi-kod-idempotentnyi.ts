class StockConsumer {
  constructor(private db: Db) {}   // приватна база сервісу складу

  // Викликається чергою на кожну доставлену подію OrderPlaced.
  async onOrderPlaced(evt: { eventId: string; payload: OrderPlacedBody }): Promise<void> {
    await this.db.transaction(async (tx) => {
      // 1) ДЕДУП: пробуємо застовпити eventId. Первинний ключ на
      //    processed_events робить повторну вставку неможливою — другий
      //    прохід тієї самої події тут спіткнеться, і ми просто вийдемо.
      const fresh = await tx.tryInsert("processed_events", {
        event_id: evt.eventId,
        handled_at: new Date(),
      });
      if (!fresh) return;   // вже бачили цей eventId — дубль, тихо виходимо

      // 2) ДІЯ: списуємо товар. У ТІЙ САМІЙ транзакції, що й відмітка дедупу,
      //    тож «оброблено» і «списано» або сталися разом, або не сталися.
      for (const item of evt.payload.items) {
        await tx.execute(
          "UPDATE stock SET qty = qty - ? WHERE sku = ? AND qty >= ?",
          [item.qty, item.sku, item.qty],
        );
      }
    }); // ← коміт: дедуп і списання нероздільні
  }
}
