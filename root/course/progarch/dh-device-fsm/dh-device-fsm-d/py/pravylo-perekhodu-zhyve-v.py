class Device:
    def __init__(self) -> None:
        self._status = DeviceStatus.NEW          # закрите поле
        self._home_id: HomeId | None = None

    def commission(self, home_id: HomeId) -> None:
        if self._status is not DeviceStatus.NEW:
            raise DomainError("пристрій уже введено в дім")
        self._status = DeviceStatus.ONLINE
        self._home_id = home_id

    def mark_offline(self) -> None:
        if self._status is DeviceStatus.OFFLINE:
            return                                # уже мовчить — тихий no-op
        if self._status is not DeviceStatus.ONLINE:
            raise DomainError("мовчати може лише пристрій, що був на зв'язку")
        self._status = DeviceStatus.OFFLINE

    def mark_online(self) -> None:
        if self._status is DeviceStatus.ONLINE:
            return
        if self._status is not DeviceStatus.OFFLINE:
            raise DomainError("на зв'язок вертається лише offline-пристрій")
        self._status = DeviceStatus.ONLINE

    def retire(self) -> None:
        if self._status is DeviceStatus.RETIRED:
            return                                # ідемпотентно
        if self._status is DeviceStatus.NEW:
            raise DomainError("ще не введений пристрій не списують")
        self._status = DeviceStatus.RETIRED       # з online чи offline — назавжди
