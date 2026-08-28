# device_lifecycle.py — АГРЕГАТ життєвого циклу. Стан, таблиця й події — в одному місці.
from dataclasses import dataclass
from enum import Enum
import time

class Status(str, Enum):
    NEW = "new"; ONLINE = "online"; OFFLINE = "offline"; RETIRED = "retired"

COMMANDS = ("commission", "markOffline", "markOnline", "retire")

# Єдине джерело правди: (стан, команда) → новий стан. Лише переходи, що МІНЯЮТЬ стан.
TRANSITIONS = {
    (Status.NEW,     "commission"):  Status.ONLINE,
    (Status.ONLINE,  "markOffline"): Status.OFFLINE,
    (Status.OFFLINE, "markOnline"):  Status.ONLINE,
    (Status.ONLINE,  "retire"):      Status.RETIRED,
    (Status.OFFLINE, "retire"):      Status.RETIRED,
}
# «Уже в цільовому стані» → тихий no-op. commission сюди НЕ входить.
IDEMPOTENT = {
    "markOffline": Status.OFFLINE,
    "markOnline":  Status.ONLINE,
    "retire":      Status.RETIRED,
}

class DomainError(Exception): ...

# Доменні події — незмінні факти «щось СТАЛОСЯ».
@dataclass(frozen=True)
class DeviceCommissioned: device_id: str; home_id: str; at: float
@dataclass(frozen=True)
class DeviceWentOffline:  device_id: str; at: float
@dataclass(frozen=True)
class DeviceReconnected:  device_id: str; at: float
@dataclass(frozen=True)
class DeviceRetired:      device_id: str; at: float

class Device:
    def __init__(self, device_id: str):
        self.id = device_id
        self._status = Status.NEW
        self._home_id = None
        self._events = []                            # зібрані, ще не опубліковані

    # Ядро: єдиний прохід крізь таблицю. Вартовий + запис події.
    def _apply(self, cmd, make):
        if IDEMPOTENT.get(cmd) == self._status:      # уже там — тихо, без події
            return
        nxt = TRANSITIONS.get((self._status, cmd))
        if nxt is None:
            raise DomainError(f"з «{self._status.value}» команда «{cmd}» неможлива")
        self._status = nxt
        self._events.append(make())                  # подія на КОЖНОМУ переході

    def commission(self, home_id, at=None):
        at = time.time() if at is None else at
        self._apply("commission", lambda: DeviceCommissioned(self.id, home_id, at))
        self._home_id = home_id                      # досяжне лише при реальному переході

    def mark_offline(self, at=None):
        at = time.time() if at is None else at
        self._apply("markOffline", lambda: DeviceWentOffline(self.id, at))

    def mark_online(self, at=None):
        at = time.time() if at is None else at
        self._apply("markOnline", lambda: DeviceReconnected(self.id, at))

    def retire(self, at=None):
        at = time.time() if at is None else at
        self._apply("retire", lambda: DeviceRetired(self.id, at))

    @property
    def state(self): return self._status
    def pull_events(self):
        out, self._events = self._events, []         # забрати й спорожнити
        return out
