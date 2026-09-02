"""Спільне налаштування тестів.

Згенерований парсер лежить поза цією текою — його кладе кодогенератор:

    ksc -t python ksy/telemetry_protocol.ksy --outdir generated/python

Тому sys.path доводиться доповнити тут. Якщо генерації не було, тести
з розміткою kaitai пропускаються, а рамкування, CRC, серіалізація й
конверт перевіряються все одно: вони чистий Python і від ksc не залежать.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

PY_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_DIR = PY_DIR.parent
GENERATED_DIR = PROJECT_DIR / "generated" / "python"

for path in (PY_DIR, GENERATED_DIR):
    if path.is_dir() and str(path) not in sys.path:
        sys.path.insert(0, str(path))


def generated_available() -> bool:
    """Чи є на місці машинний вихід ksc разом із рантаймом kaitaistruct."""
    from importlib.util import find_spec

    try:
        return find_spec("telemetry_protocol") is not None and find_spec("kaitaistruct") is not None
    except (ImportError, ValueError):
        return False


requires_generated = pytest.mark.skipif(
    not generated_available(),
    reason="немає generated/python: спершу ksc -t python ksy/telemetry_protocol.ksy",
)


@pytest.fixture(scope="session")
def parser_class():
    """Клас згенерованого парсера; без нього тест не має сенсу — пропускаємо."""
    module = pytest.importorskip(
        "telemetry_protocol",
        reason="спершу ksc -t python ksy/telemetry_protocol.ksy --outdir generated/python",
    )
    return module.TelemetryProtocol
