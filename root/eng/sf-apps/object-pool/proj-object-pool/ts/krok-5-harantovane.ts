class Pool<T> {
  // ... acquire / release ...

  async use<R>(fn: (obj: T) => Promise<R>): Promise<R> {
    const obj = await this.acquire();     // позичив
    try {
      return await fn(obj);               // віддав користувачеві
    } finally {
      this.release(obj);                  // повернув — на будь-якому виході,
    }                                     // навіть якщо fn кинув виняток
  }
}

// використання: об'єкт живе рівно стільки, скільки триває колбек
await pool.use(async (conn) => {
  const rows = await conn.query("select ...");
  if (rows.length === 0) return null;     // release однаково станеться
  return process(rows);
});
