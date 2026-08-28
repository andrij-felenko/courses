import sqlite3, datetime

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

# Історія схеми: (версія, нотатка, список операторів). Порядок — за версією, залізно.
MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (1, "реєстр DH переїжджає з памʼяті на диск", [
        """CREATE TABLE home (
               id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
               plan TEXT NOT NULL DEFAULT 'free',
               device_cap INTEGER NOT NULL DEFAULT 5,
               used_slots INTEGER NOT NULL DEFAULT 0 CHECK (used_slots >= 0),
               threshold  REAL NOT NULL DEFAULT 20.0,
               CHECK (used_slots <= device_cap))""",
        """CREATE TABLE device (
               id TEXT PRIMARY KEY,
               home_id TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,
               kind TEXT NOT NULL CHECK (kind IN ('lock','thermostat','plug','sensor')),
               room TEXT NOT NULL, state TEXT NOT NULL, paired_at TEXT NOT NULL)""",
    ]),
    (2, "телеметрія дістає власну таблицю (за портом TelemetrySink)", [
        """CREATE TABLE measurement (
               device_id TEXT NOT NULL, ts REAL NOT NULL, value REAL NOT NULL,
               PRIMARY KEY (device_id, ts))""",
    ]),
    # (3, "годинник останньої активності", ["ALTER TABLE device ADD COLUMN last_seen TEXT"]),
]

def run_migrations(conn: sqlite3.Connection) -> int:
    """Накотити всі міграції, яких ще нема на цій базі. Ідемпотентно: повторний виклик — no-op."""
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version ("
                 "  version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, note TEXT)")
    current = conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
    for version, note, statements in sorted(MIGRATIONS, key=lambda m: m[0]):   # ← ПОРЯДОК
        if version <= current:
            continue                             # уже накатано — пропускаємо
        conn.execute("BEGIN")                    # схема Й відмітка версії — в ОДНІЙ транзакції
        try:
            for sql in statements:
                conn.execute(sql)
            conn.execute("INSERT INTO schema_version(version, applied_at, note) VALUES(?,?,?)",
                         (version, _now(), note))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")             # напів-накоченої схеми не існує
            raise
    return conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
