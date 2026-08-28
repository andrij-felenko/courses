import sqlite3

def open_registry(path: str) -> sqlite3.Connection:
    """Писар реєстру й бюджету: тривкість по максимуму."""
    c = sqlite3.connect(path, isolation_level=None)   # ми САМІ керуємо BEGIN/COMMIT
    c.execute("PRAGMA journal_mode = WAL")            # властивість ФАЙЛУ — досить раз на базу
    c.execute("PRAGMA synchronous  = FULL")          # властивість ЦЬОГО зʼєднання: fsync на кожен коміт
    c.execute("PRAGMA foreign_keys = ON")            # SQLite інакше НЕ стежить за FK (див. пастки)
    c.execute("PRAGMA busy_timeout = 5000")          # писар ЧЕКАЄ замок, а не падає з SQLITE_BUSY
    return c

def open_telemetry(path: str) -> sqlite3.Connection:
    """Писар телеметрії: тривкість свідомо відпущена заради пропускної."""
    c = sqlite3.connect(path, isolation_level=None)
    c.execute("PRAGMA journal_mode = WAL")            # той самий файл — WAL уже стоїть, рядок безкоштовний
    c.execute("PRAGMA synchronous  = NORMAL")        # НЕ fsync на кожен коміт: хвіст під ризиком на відмові живлення
    c.execute("PRAGMA busy_timeout = 5000")
    return c
