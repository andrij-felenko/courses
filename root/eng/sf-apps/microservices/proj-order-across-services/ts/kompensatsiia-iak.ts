// Компенсація на боці СКЛАДУ: повертаємо раніше списаний товар.
class StockConsumer {
  // ... onOrderPlaced як вище ...

  async onOrderCancelled(evt: { eventId: string; payload: OrderCancelledBody }): Promise<void> {
    await this.db.transaction(async (tx) => {
      // та сама дедуплікація — компенсація теж має бути безпечною до повтору
      const fresh = await tx.tryInsert("processed_events", {
        event_id: evt.eventId, handled_at: new Date(),
      });
      if (!fresh) return;

      // КОМПЕНСАЦІЯ: дописуємо товар назад — логічний антипод списання
      for (const item of evt.payload.items) {
        await tx.execute(
          "UPDATE stock SET qty = qty + ? WHERE sku = ?", [item.qty, item.sku],
        );
      }
    });
  }
}
