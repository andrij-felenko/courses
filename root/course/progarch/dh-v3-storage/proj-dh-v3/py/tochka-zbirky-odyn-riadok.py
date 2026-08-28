def connect(path: str, synchronous: str = "FULL") -> sqlite3.Connection:
    c = sqlite3.connect(path, isolation_level=None)   # ми САМІ керуємо BEGIN/COMMIT
    c.execute("PRAGMA journal_mode = WAL")            # властивість файлу — досить раз на базу
    c.execute(f"PRAGMA synchronous = {synchronous}")  # FULL для реєстру, NORMAL для телеметрії
    c.execute("PRAGMA foreign_keys = ON")             # SQLite інакше НЕ стежить за FK!
    c.execute("PRAGMA busy_timeout = 5000")           # писар ЧЕКАЄ замок, а не падає з BUSY
    return c

def build(path: str) -> HubService:                   # ТОЧКА ЗБІРКИ
    reg = connect(path, "FULL")                       # реєстр: тривкість по максимуму
    run_migrations(reg)                               # схема доганяє код: 001 переселив реєстр на диск
    devices = SqliteDeviceRepository(reg)             # ← ОДИН РЯДОК: SQLite стала за DeviceRepository
    #   було: devices = InMemoryDeviceRepository()    #   (v2 — тимчасова затичка в памʼяті)
    telemetry = SqliteTelemetrySink(connect(path, "NORMAL"))   # той самий файл, відпущена тривкість
    return HubService(sensor=OneWireThermometer(...), heater=SmartPlug(...),
                      devices=devices, telemetry=telemetry, cfg=Config(threshold=20.0))
