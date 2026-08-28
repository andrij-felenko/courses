import { DatabaseSync } from "node:sqlite";

export class SqliteStore implements ReadingStore {
  private db = new DatabaseSync(":memory:");
  constructor() {
    // стовпець at — INTEGER: сховище тримає ЦІЛІ мілісекунди
    this.db.exec("CREATE TABLE readings (at INTEGER NOT NULL, celsius REAL NOT NULL)");
  }
  save(r: Reading): void {
    this.db.prepare("INSERT INTO readings (at, celsius) VALUES (?, ?)")
      .run(Math.round(r.at), r.celsius);          // округлюємо на вході — стовпець цілий
  }
  recent(limit: number): Reading[] {
    const rows = this.db
      .prepare("SELECT at, celsius FROM readings ORDER BY at DESC LIMIT ?")
      .all(limit) as Array<{ at: number; celsius: number }>;
    return rows.map(r => ({ at: r.at, celsius: r.celsius }));
  }
}
