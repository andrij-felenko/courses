# ── 3. Порт у фізичний світ + зведення бажаного до справжнього ──
from dataclasses import field
from typing import Protocol


@dataclass(frozen=True)
class Acked:                            # замок відповів — і ось його справжній стан
    state: LockState

@dataclass(frozen=True)
class Offline:                          # не на зв'язку — правди не знаємо
    pass

LockOutcome = Acked | Offline           # розмічене об'єднання (3.10+)


class DeviceGateway(Protocol):          # порт: єдиний місток до заліза
    def send_lock(self, id: DeviceId) -> LockOutcome: ...


@dataclass(frozen=True)
class ReconcileReport:                  # чесний знімок ОДНОГО проходу — значення
    desired: HomeMode
    locked: list[DeviceId]
    offline: list[DeviceId]             # не підтвердили замкнення цього проходу
    jammed: list[DeviceId]              # потрібна людина

    @property
    def settled(self) -> bool:
        return not self.offline and not self.jammed

    def __str__(self) -> str:
        off = ", ".join(map(str, self.offline)) or "—"
        jam = f" · заклинило: {', '.join(map(str, self.jammed))}" if self.jammed else ""
        return f"[{self.desired.value}] {len(self.locked)} замкнено · офлайн: {off}{jam}"


class AwayReconciler:
    def __init__(self, gateway: DeviceGateway):
        self._gateway = gateway

    # Зводить БАЖАНЕ (режим дому) до СПРАВЖНЬОГО (стан кожного замка).
    # Це НЕ транзакція — це один прохід циклу, що доганяє.
    def sweep(self, home: Home, locks: dict[str, Lock]) -> ReconcileReport:
        locked: list[DeviceId] = []
        offline: list[DeviceId] = []
        jammed: list[DeviceId] = []
        if home.mode not in (HomeMode.AWAY, HomeMode.NIGHT):
            return ReconcileReport(home.mode, locked, offline, jammed)

        for id in home.locks:
            lock = locks.get(id.value)
            if lock is None:
                continue
            match self._gateway.send_lock(id):          # команда пішла в залізо
                case Offline():
                    offline.append(id)                  # лишаємо останнє відоме, повторимо
                case Acked(state=LockState.LOCKED):
                    lock.report_from_device(LockState.LOCKED)
                    locked.append(id)
                case Acked(state=LockState.JAMMED):
                    lock.report_from_device(LockState.JAMMED)
                    jammed.append(id)
                case Acked(state=other):
                    lock.report_from_device(other)      # відповів, але не замкнувся
                    offline.append(id)                  # у чергу на повтор
        return ReconcileReport(home.mode, locked, offline, jammed)
