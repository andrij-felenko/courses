class SqlTransactionManager implements TransactionManager {
  constructor(private readonly pool: Pool) {}

  async run<T>(work: () => Promise<T>): Promise<T> {
    const conn = await this.pool.connect();
    await conn.query("BEGIN");
    try {
      const result = await work();     // усі кроки сценарію — тут
      await conn.query("COMMIT");      // дійшли без винятку → закріпити
      return result;
    } catch (e) {
      await conn.query("ROLLBACK");    // будь-який збій → відкотити все
      throw e;                         // і проштовхнути помилку далі
    } finally {
      conn.release();                  // з'єднання завжди повертається в пул
    }
  }
}
