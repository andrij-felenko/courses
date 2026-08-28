# ── 2. Сутності-корені малих агрегатів ──
class Lock:                                     # СУТНІСТЬ + корінь свого агрегата
    def __init__(self, id: DeviceId, home_id: HomeId, location: Location):
        self.id = id
        self.home_id = home_id                  # ← власника вимагає конструктор:
        self.location = location                #    інваріант 1 «не буває нічий»
        self._state = LockState.UNKNOWN         # завжди визначений (інваріант 2)

    # Локальний НАМІР (кнопка в застосунку). Заклинений — командою не чіпаємо.
    def lock(self) -> None:
        if self._state is LockState.JAMMED:
            raise DomainError(f"замок {self.id} заклинило — командою не замкнути, спершу ремонт")
        self._state = LockState.LOCKED

    def unlock(self) -> None:
        if self._state is LockState.JAMMED:
            raise DomainError(f"замок {self.id} заклинило — командою не відчинити")
        self._state = LockState.UNLOCKED

    # ПРАВДА з поля: фізика доповіла — приймаємо як є (навіть Jammed).
    def report_from_device(self, s: LockState) -> None:
        self._state = s

    def is_locked(self) -> bool:
        return self._state is LockState.LOCKED

    @property
    def current(self) -> LockState:
        return self._state


class Home:                                     # окремий МАЛИЙ агрегат
    def __init__(self, id: HomeId, owner_id: UserId):
        self.id = id
        self.owner_id = owner_id                # дім не буває без власника
        self._mode = HomeMode.HOME
        self._room_ids: list[RoomId] = []
        self._member_ids: list[UserId] = []
        self._lock_ids: list[DeviceId] = []     # ← лише id, НЕ живі об'єкти замків

    def set_mode(self, m: HomeMode) -> None:
        self._mode = m                          # міняє СВІЙ стан — і тільки

    @property
    def mode(self) -> HomeMode:
        return self._mode

    def add_room(self, r: RoomId) -> None: self._room_ids.append(r)
    def admit(self, u: UserId) -> None: self._member_ids.append(u)
    def attach_lock(self, d: DeviceId) -> None: self._lock_ids.append(d)

    @property
    def locks(self) -> list[DeviceId]:
        return list(self._lock_ids)
