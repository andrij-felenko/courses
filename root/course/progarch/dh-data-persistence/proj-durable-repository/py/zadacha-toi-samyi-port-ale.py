from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Device:                         # доменний пристрій із реєстру — тепер з ключем
    id: str                           # стабільний ідентифікатор, напр. "lock-1"
    kind: str                         # "lock", "plug", "thermostat"…
    room: str
    state: str = "unknown"

    def to_dict(self) -> dict:        # плаский рядок для серіалізації у файл
        return {"id": self.id, "kind": self.kind, "room": self.room, "state": self.state}

    @staticmethod
    def from_dict(r: dict) -> "Device":
        return Device(r["id"], r["kind"], r["room"], r.get("state", "unknown"))

class DeviceRepository(Protocol):     # ПОРТ: три обіцянки, і жодного слова про носій
    def save(self, d: Device) -> None: ...          # поклади (або онови за id)
    def get(self, id: str) -> Device | None: ...    # дай один за ключем, або нічого
    def all(self) -> list[Device]: ...              # дай усіх
