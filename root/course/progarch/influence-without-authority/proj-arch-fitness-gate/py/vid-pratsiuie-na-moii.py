import os, re
from pathlib import Path

ROOT = Path("src")
ADAPTER = ROOT / "storage"                              # єдине легальне місце драйвера
DRIVER = re.compile(r"^\s*(from\s+psycopg\b|import\s+psycopg\b)", re.M)  # САМЕ import psycopg
IGNORE = ("_test.py", "/migrations/")                   # законні винятки — не наша межа
ADR = "docs/adr/0007-telemetry-store.md"
MODE = os.environ.get("ARCH_MODE", "gate")              # warn | gate

def _offends(p: Path) -> bool:
    if ADAPTER in p.parents or any(s in p.as_posix() for s in IGNORE):
        return False
    return bool(DRIVER.search(p.read_text(encoding="utf-8")))

def offenders() -> list[str]:
    return sorted(p.relative_to(ROOT).as_posix()
                  for p in ROOT.rglob("*.py") if _offends(p))

def report(fresh: list[str]) -> None:
    print(f"\nДрайвер БД імпортовано поза storage/ ({len(fresh)}):")
    for p in fresh:
        print(f"  src/{p}")
    print("\n  Мощена дорога: TelemetryStore.energy_by_period() — інтерфейс тримає базу замінною.")
    print(f"  Чому саме так:  {ADR}\n")
