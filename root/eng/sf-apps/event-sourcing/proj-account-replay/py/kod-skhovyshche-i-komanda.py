from dataclasses import dataclass
from datetime import datetime, timezone

# Тіло події — доконаний факт. Мінімум полів: що і на скільки.
@dataclass(frozen=True)
class Deposited:
    amount: float

@dataclass(frozen=True)
class Withdrawn:
    amount: float

@dataclass(frozen=True)
class FeeCharged:
    amount: float

# Збережена подія = тіло + метадані потоку. version — позиція в потоці (з 1).
@dataclass(frozen=True)
class Stored:
    stream_id: str
    version: int            # 1, 2, 3, … — монотонно росте в межах потоку
    event: object
    at: str                 # мітка часу, знадобиться темпоральним запитам

# Сигнал конфлікту версій — окремий виняток, щоб виклик міг його спіймати й повторити.
class VersionConflict(Exception):
    def __init__(self, expected: int, actual: int):
        super().__init__(f"очікували версію {expected}, а потік уже на {actual}")
        self.expected, self.actual = expected, actual

class EventStore:
    # У реальності — таблиця (stream_id, version, payload) з PK (stream_id, version).
    # Тут — просто список на потік.
    def __init__(self):
        self._streams: dict[str, list[Stored]] = {}

    # Прочитати весь потік (для згортання й для перевірки версії).
    def read(self, stream_id: str) -> list[Stored]:
        return self._streams.get(stream_id, [])

    # Поточна версія потоку = скільки в ньому подій.
    def current_version(self, stream_id: str) -> int:
        return len(self.read(stream_id))

    # ОСЕРДЯ append-only. Дописати нові події ТІЛЬКИ якщо потік досі на expected_version.
    def append(self, stream_id: str, expected_version: int, events: list) -> list[Stored]:
        stream = self._streams.get(stream_id, [])
        actual = len(stream)
        if actual != expected_version:
            # Хтось дописав між нашим читанням і цим записом — відхиляємо, хай повторить.
            raise VersionConflict(expected_version, actual)
        now = datetime.now(timezone.utc).isoformat()
        appended = [Stored(stream_id, actual + i + 1, ev, now)
                    for i, ev in enumerate(events)]
        self._streams[stream_id] = stream + appended
        return appended                # ніколи не міняємо старе — лише додаємо
