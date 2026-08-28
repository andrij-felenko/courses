import re, sys
from pathlib import Path

ADAPTER = Path("src") / "storage"           # єдине легальне місце для драйвера БД
DRIVER = re.compile(r"^\s*(import\s+psycopg|from\s+psycopg\b)", re.M)

offenders = [
    p for p in Path("src").rglob("*.py")
    if ADAPTER not in p.parents
    and DRIVER.search(p.read_text(encoding="utf-8"))
]

if offenders:
    print("Драйвер БД імпортовано поза storage/:")
    for p in offenders:
        print(f"  {p}")
    print("Ходи через TelemetryStore.energy_by_period() — інтерфейс тримає базу замінною.")
    sys.exit(1)               # білд червоний: правило тримає перевірка, не людина
