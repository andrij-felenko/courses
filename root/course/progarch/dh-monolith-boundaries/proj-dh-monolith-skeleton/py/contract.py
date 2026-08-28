# telemetry/contract.py — ПУБЛІЧНЕ: те, що бачать сусіди
from dataclasses import dataclass
from ids import DeviceId
@dataclass(frozen=True)
class Reading:
    device_id: DeviceId
    value: float
    at: int

# telemetry/_store.py — ПРИВАТНЕ (під підкресленням): лише цей модуль торкається схеми telemetry
from ids import DeviceId
from .contract import Reading
class _ReadingStore:
    def __init__(self, schema):                    # schema = дескриптор ЛИШЕ схеми telemetry
        self._s = schema
        schema.execute("""CREATE TABLE IF NOT EXISTS telemetry.reading(
                            device_id TEXT, value DOUBLE PRECISION, at BIGINT)""")
    def put(self, r: Reading) -> None:
        self._s.execute("INSERT INTO telemetry.reading(device_id, value, at) VALUES (%s,%s,%s)",
                        (r.device_id, r.value, r.at))
    def last(self, device_id: DeviceId) -> Reading | None:
        row = self._s.query_one("SELECT value, at FROM telemetry.reading "
                                "WHERE device_id=%s ORDER BY at DESC LIMIT 1", (device_id,))
        return Reading(device_id, row.value, row.at) if row else None

# telemetry/_service.py — реалізація фасаду (клас доступний, фабрика — офіційні двері)
from ids import DeviceId, DeviceEvent
from .contract import Reading
from ._store import _ReadingStore
class Telemetry:                                    # ← ФАСАД
    def __init__(self, store: _ReadingStore):
        self._store = store
    def record(self, e: DeviceEvent) -> None:       # підписник шини
        if e.kind == "state":
            self._store.put(Reading(e.device_id, e.value, e.at))
    def last_reading(self, device_id: DeviceId) -> Reading | None:
        return self._store.last(device_id)
def make_telemetry(schema) -> Telemetry:            # фабрика в'яже приватний стор зі схемою
    return Telemetry(_ReadingStore(schema))

# telemetry/__init__.py — БАР'ЄР: назовні видно лише фасад, фабрику й публічний контракт
from ._service import Telemetry, make_telemetry
from .contract import Reading
__all__ = ["Telemetry", "make_telemetry", "Reading"]
