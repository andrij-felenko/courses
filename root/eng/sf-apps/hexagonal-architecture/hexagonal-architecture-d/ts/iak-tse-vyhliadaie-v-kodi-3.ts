// ── ДРАЙВОВАНИЙ АДАПТЕР: реалізує вихідний порт мовою Postgres ──
class PgЗамовленняСховище implements ЗамовленняСховище {
  constructor(private db: PgPool) {}
  async зберегти(з: Замовлення): Promise<void> {
    await this.db.query(                       // ось тут — і тільки тут — SQL
      "INSERT INTO orders(id, email, total) VALUES ($1,$2,$3)",
      [з.id, з.пошта, з.сума()],
    );
  }
}
