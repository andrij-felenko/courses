class OutboxRelay {
  constructor(private db: Db, private queue: Queue) {}

  // Викликається за розкладом (напр. кожні 200 мс) або петлею.
  async flush(): Promise<void> {
    const rows = await this.db.query(
      "SELECT * FROM outbox WHERE sent = false ORDER BY created_at LIMIT 100",
    );

    for (const row of rows) {
      // Публікуємо ПЕРЕД тим, як позначити sent. Якщо впадемо між
      // publish і update — рядок лишиться sent=false, і наступний
      // прохід надішле його ЩЕ раз. Дубль на боці споживача безпечний
      // (він ідемпотентний), а от ВТРАТА події — ні. Тому саме такий порядок.
      await this.queue.publish(row.topic, {
        eventId: row.event_id,      // той самий ключ дедуплікації
        payload: JSON.parse(row.payload),
      });
      await this.db.execute(
        "UPDATE outbox SET sent = true WHERE event_id = ?", [row.event_id],
      );
    }
  }
}
