// adapters/pg.ts ── ДРАЙВОВАНИЙ АДАПТЕР. Реалізує ЗамовленняСховище через Postgres.
import { ЗамовленняСховище, Замовлення } from "../order/core";

export class PgСховище implements ЗамовленняСховище {
  constructor(private db: PgPool) {}

  async зберегти(з: Замовлення): Promise<void> {
    await this.db.query(                       // ← SQL живе ТІЛЬКИ в цьому файлі
      `INSERT INTO orders(id, email, positions, total)
       VALUES ($1, $2, $3, $4)`,
      [з.id, з.пошта, JSON.stringify(з.позиції), з.сума()],
    );
  }

  async узяти(id: string): Promise<Замовлення | null> {
    const r = await this.db.query("SELECT * FROM orders WHERE id = $1", [id]);
    if (r.rows.length === 0) return null;
    const рядок = r.rows[0];
    return Замовлення.створити(рядок.id, рядок.email, JSON.parse(рядок.positions));
  }
}
