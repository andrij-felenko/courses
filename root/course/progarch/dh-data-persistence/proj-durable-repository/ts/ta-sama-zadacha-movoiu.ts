import { DatabaseSync } from "node:sqlite";         // вбудований у Node ≥ 22.5

class SqliteDeviceRepository {                      // ТОЙ САМИЙ порт DeviceRepository
  private db: DatabaseSync;
  constructor(path = "dh.db") {
    this.db = new DatabaseSync(path);
    this.db.exec("PRAGMA journal_mode=WAL");        // читачі не блокують писаря
    this.db.exec(`CREATE TABLE IF NOT EXISTS devices (
      id    TEXT PRIMARY KEY,                        -- ключ реєстру — на рівні схеми
      kind  TEXT NOT NULL,
      room  TEXT NOT NULL,
      state TEXT NOT NULL)`);
  }

  save(d: Device): void {
    this.db.prepare(
      `INSERT INTO devices (id, kind, room, state) VALUES (?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET               -- поклади АБО онови за id
         kind=excluded.kind, room=excluded.room, state=excluded.state`
    ).run(d.id, d.kind, d.room, d.state);           // run() автокомітить → тривко
  }
  get(id: string): Device | undefined {
    return this.db.prepare(
      "SELECT id, kind, room, state FROM devices WHERE id = ?"
    ).get(id) as Device | undefined;                // частковий пошук за ключем
  }
  all(): Device[] {
    return this.db.prepare(
      "SELECT id, kind, room, state FROM devices").all() as Device[];
  }
}
