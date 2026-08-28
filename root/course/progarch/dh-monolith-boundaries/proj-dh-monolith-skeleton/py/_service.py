# control/_service.py — команда й розсилка події в ОДНІЙ транзакції
from time import time
from ids import Bus, DeviceEvent
from ._store import _DeviceRepo
from .contract import Command
class Control:
    def __init__(self, repo: _DeviceRepo, bus: Bus):
        self._repo, self._bus = repo, bus
    def apply(self, cmd: Command) -> None:
        with self._repo.tx() as tx:                 # ← одна транзакція на всю операцію
            device = self._repo.apply(cmd, tx)      # приватна нутрощі: пише в схему control
            self._bus.publish(DeviceEvent(          # підписники біжать ТУТ-ТАКИ, у цій tx
                kind="state", device_id=device.id, home_id=device.home_id,
                at=int(time() * 1000), value=device.state))
        # нормальний вихід із with = COMMIT; будь-який виняток усередині = ROLLBACK усього
def make_control(schema, bus: Bus) -> Control:
    return Control(_DeviceRepo(schema), bus)
