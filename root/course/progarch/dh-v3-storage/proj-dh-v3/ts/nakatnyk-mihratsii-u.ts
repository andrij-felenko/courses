import { DatabaseSync } from "node:sqlite";       // вбудований у Node ≥ 22.5

const now = () => new Date().toISOString();

// Історія схеми: [версія, нотатка, оператори]. Порядок — за версією, залізно.
const MIGRATIONS: [number, string, string[]][] = [
  [1, "реєстр DH переїжджає з памʼяті на диск", [
    `CREATE TABLE home (
        id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
        plan TEXT NOT NULL DEFAULT 'free',
        device_cap INTEGER NOT NULL DEFAULT 5,
        used_slots INTEGER NOT NULL DEFAULT 0 CHECK (used_slots >= 0),
        threshold  REAL NOT NULL DEFAULT 20.0,
        CHECK (used_slots <= device_cap))`,
    `CREATE TABLE device (
        id TEXT PRIMARY KEY,
        home_id TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('lock','thermostat','plug','sensor')),
        room TEXT NOT NULL, state TEXT NOT NULL, paired_at TEXT NOT NULL)`,
  ]],
  [2, "телеметрія дістає власну таблицю (за портом TelemetrySink)", [
    `CREATE TABLE measurement (
        device_id TEXT NOT NULL, ts REAL NOT NULL, value REAL NOT NULL,
        PRIMARY KEY (device_id, ts))`,
  ]],
  // [3, "годинник останньої активності", ["ALTER TABLE device ADD COLUMN last_seen TEXT"]],
];

function runMigrations(db: DatabaseSync): number {   // ідемпотентно: повторний виклик — no-op
  db.exec("CREATE TABLE IF NOT EXISTS schema_version ("
        + "  version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, note TEXT)");
  const current = db.prepare(
    "SELECT COALESCE(MAX(version), 0) AS v FROM schema_version").get() as { v: number };
  const ins = db.prepare("INSERT INTO schema_version(version, applied_at, note) VALUES(?,?,?)");
  for (const [version, note, statements] of [...MIGRATIONS].sort((a, b) => a[0] - b[0])) {
    if (version <= current.v) continue;              // уже накатано — пропускаємо
    db.exec("BEGIN");                                // схема Й відмітка — в ОДНІЙ транзакції
    try {
      for (const sql of statements) db.exec(sql);
      ins.run(version, now(), note);
      db.exec("COMMIT");
    } catch (e) { db.exec("ROLLBACK"); throw e; }    // напів-накоченої схеми не існує
  }
  return (db.prepare("SELECT COALESCE(MAX(version),0) AS v FROM schema_version")
            .get() as { v: number }).v;
}
