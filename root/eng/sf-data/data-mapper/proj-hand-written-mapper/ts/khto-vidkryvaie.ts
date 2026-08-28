// ── шов, у який потім стане транзакція ─────────────────────────
interface Executor {
  one<T>(sql: string, args: unknown[]): Promise<T | null>;
  all<T>(sql: string, args: unknown[]): Promise<T[]>;
  run(sql: string, args: unknown[]): Promise<{ rowCount: number }>;
}

interface Pool {
  connect(): Promise<Executor & { release(): void }>;
}

async function withTransaction<T>(pool: Pool, fn: (tx: Executor) => Promise<T>): Promise<T> {
  const conn = await pool.connect();
  try {
    await conn.run("BEGIN", []);
    const out = await fn(conn);
    await conn.run("COMMIT", []);
    return out;
  } catch (err) {
    // з'єднання могло вже вмерти — хай ROLLBACK не затуляє справжню помилку
    await conn.run("ROLLBACK", []).catch(() => {});
    throw err;
  } finally {
    conn.release();
  }
}
