// dh-jobs.ts — робочий маршрутизатор фонових задач DH.  Запуск: npx tsx dh-jobs.ts

type Row = Record<string, unknown>;

// Мінімальна, але ЧЕСНА модель БД: вставлене в транзакції видно лише після commit().
class Db {
  private tables = new Map<string, Row[]>();
  table(name: string): Row[] {
    if (!this.tables.has(name)) this.tables.set(name, []);
    return this.tables.get(name)!;                 // закомічені рядки цієї таблиці
  }
  begin(): Tx { return new Tx(this); }
}

class Tx {
  private staged: { table: string; row: Row }[] = [];   // буфер: ще НЕ закомічені вставки
  private done = false;
  constructor(private db: Db) {}
  insert(table: string, row: Row): void {
    if (this.done) throw new Error("транзакція вже завершена");
    this.staged.push({ table, row });              // просто складаємо в буфер — у таблицю ще нічого
  }
  commit(): void {
    if (this.done) throw new Error("подвійний commit");
    for (const { table, row } of this.staged)      // одним махом: усе або нічого
      this.db.table(table).push(row);
    this.done = true;
  }
  rollback(): void {
    this.staged = [];                              // викидаємо буфер — жоден рядок не осів
    this.done = true;
  }
}

// Ідіоматична обгортка: коміт на успіх, відкат на будь-який виняток.
function withTransaction(db: Db, body: (tx: Tx) => void): void {
  const tx = db.begin();
  try { body(tx); tx.commit(); }
  catch (e) { tx.rollback(); throw e; }            // впало до commit → нічого не осіло
}
