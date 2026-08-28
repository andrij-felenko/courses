class Lock:                                     # СУТНІСТЬ + корінь свого агрегата
    def __init__(self, id: DeviceId, home_id: "HomeId", room_id: "RoomId"):
        self.id = id
        self.home_id = home_id                  # ← власника вимагають при народженні:
        self.room_id = room_id                  #    інваріант 1 «не буває нічий»
        self._state = LockState.UNKNOWN         # завжди визначений — інваріант 2

    # Єдині двері всередину: стан міняють лише через них.
    def lock(self) -> None:
        if self._state is LockState.JAMMED:
            raise DomainError("заклинений замок не замкнути — спершу ремонт")
        self._state = LockState.LOCKED

    def unlock(self) -> None:
        if self._state is LockState.JAMMED:
            raise DomainError("заклинений замок не відчинити командою")
        self._state = LockState.UNLOCKED

    def report_from_device(self, s: LockState) -> None:
        self._state = s                         # фізика доповіла — приймаємо як є

    def is_locked(self) -> bool:
        return self._state is LockState.LOCKED
