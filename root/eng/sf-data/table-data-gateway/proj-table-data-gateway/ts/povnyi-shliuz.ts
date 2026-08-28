import { Pool, PoolClient, QueryResult } from "pg";

// Виконавець — усе, що вміє виконати запит: і пул, і клієнт усередині транзакції.
type Executor = { query(text: string, values?: unknown[]): Promise<QueryResult> };

type OrderRow = {
  id: number; customer_id: string; total_cents: number;
  status: string; updated_at: Date;
};

const COLS = "id, customer_id, total_cents, status, updated_at";

class OrderTableGateway {
  constructor(private readonly db: Executor) {}   // з'єднання приходить ЗЗОВНІ

  async find(id: number): Promise<OrderRow | undefined> {
    const res = await this.db.query(`SELECT ${COLS} FROM orders WHERE id = $1`, [id]);
    return res.rows[0];                            // немає рядка — undefined, не виняток
  }

  async findByStatus(status: string, limit = 500): Promise<OrderRow[]> {
    const res = await this.db.query(
      `SELECT ${COLS} FROM orders WHERE status = $1 ORDER BY id LIMIT $2`,
      [status, limit],
    );
    return res.rows;
  }

  async insert(customerId: string, totalCents: number, status: string): Promise<number> {
    const res = await this.db.query(
      `INSERT INTO orders (customer_id, total_cents, status)
       VALUES ($1, $2, $3) RETURNING id`,
      [customerId, totalCents, status],
    );
    return res.rows[0].id;                         // ключ віддає база, не код
  }

  async updateStatus(id: number, status: string): Promise<number> {
    const res = await this.db.query(
      `UPDATE orders SET status = $1, updated_at = now() WHERE id = $2`,
      [status, id],
    );
    return res.rowCount ?? 0;                      // 0 = такого рядка не було
  }

  async remove(id: number): Promise<number> {
    const res = await this.db.query(`DELETE FROM orders WHERE id = $1`, [id]);
    return res.rowCount ?? 0;
  }
}

// Межа транзакції: одна ділова дія — один BEGIN … COMMIT.
async function inTransaction<T>(pool: Pool, work: (tx: PoolClient) => Promise<T>) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const out = await work(client);
    await client.query("COMMIT");
    return out;
  } catch (e) {
    await client.query("ROLLBACK");
    throw e;                                       // помилку НЕ ковтаємо
  } finally {
    client.release();                              // клієнт вертається в пул завжди
  }
}

// Виклик: правило живе ЗОВНІ шлюзу, межа транзакції — теж зовні.
await inTransaction(pool, async (tx) => {
  const gw = new OrderTableGateway(tx);            // той самий tx на всі виклики
  for (const row of await gw.findByStatus("paid")) {
    if (row.total_cents > 100_000) await gw.updateStatus(row.id, "review");
  }
});
