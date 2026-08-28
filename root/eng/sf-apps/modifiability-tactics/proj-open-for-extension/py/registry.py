# --- registry.py: ЯДРО. Пишеться раз, на формати не відкривається ---
from typing import Protocol

Row = dict[str, object]

# Контракт розширення (порт). Ядро володіє ним; варіанти його реалізують.
class Exporter(Protocol):
    format: str
    def export(self, rows: list[Row]) -> str: ...

_registry: dict[str, Exporter] = {}

# Декоратор самозапису — ідіоматичний спосіб оголоситися в Python.
def register(cls: type) -> type:
    if cls.format in _registry:
        raise ValueError(f"формат '{cls.format}' вже зайнято")
    _registry[cls.format] = cls()          # один спільний екземпляр (він без стану)
    return cls

# Диспетчер: знайти реалізацію за форматом і делегувати. Жодного варіанта не знає.
def export_report(fmt: str, rows: list[Row]) -> str:
    exporter = _registry.get(fmt)
    if exporter is None:
        raise ValueError(f"немає експортера для '{fmt}'")
    return exporter.export(rows)           # поліморфний виклик
