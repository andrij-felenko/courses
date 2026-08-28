class Pool<T> {
  private free: T[];
  private inUse = new Set<T>();

  constructor(
    private factory: () => T,                    // як народити Conn
    private reset: (obj: T) => void,             // як його скинути
    size: number,
  ) {
    this.free = Array.from({ length: size }, () => factory());  // наперед
  }

  acquire(): T {
    const obj = this.free.pop()!;                // знімаємо з полиці
    this.inUse.add(obj);                         // → in-use
    return obj;
  }

  release(obj: T): void {
    this.reset(obj);                             // ← стерти чужий стан ДО полиці
    this.inUse.delete(obj);                      // більше не in-use
    this.free.push(obj);                         // → free, чистим
  }
}

const pool = new Pool(() => Conn.open(), (c) => c.reset(), 8);
const conn = pool.acquire();
conn.query("select 1");
pool.release(conn);                              // повернули чистим
