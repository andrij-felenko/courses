function connect(path: string, synchronous = "FULL"): DatabaseSync {
  const db = new DatabaseSync(path);
  db.exec("PRAGMA journal_mode = WAL");
  db.exec(`PRAGMA synchronous = ${synchronous}`);     // FULL для реєстру, NORMAL для телеметрії
  db.exec("PRAGMA foreign_keys = ON");                // SQLite інакше НЕ стежить за FK!
  db.exec("PRAGMA busy_timeout = 5000");
  return db;
}

function build(path: string): HubService {            // ТОЧКА ЗБІРКИ
  const reg = connect(path, "FULL");
  runMigrations(reg);                                 // 001 переселив реєстр на диск
  const devices = new SqliteDeviceRepository(reg);    // ← ОДИН РЯДОК: SQLite за DeviceRepository
  //   було: const devices = new InMemoryDeviceRepository();   // v2 — затичка в памʼяті
  const telemetry = new SqliteTelemetrySink(connect(path, "NORMAL"));
  return new HubService(new OneWireThermometer(/*…*/), new SmartPlug(/*…*/),
                        devices, telemetry, { threshold: 20.0 });
}
