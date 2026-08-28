@dataclass(frozen=True)
class HomeSnapshot:                  # DTO: плаский знімок назовні, а не живий об'єкт
    heating: bool
    devices: list[Device]

class HubService:
    def __init__(self, sensor: Sensor, heater: Heater,
                 devices: DeviceRepository, cfg: Config):
        self._sensor, self._heater = sensor, heater     # драйвовані порти — інтерфейси
        self._devices, self._cfg = devices, cfg
        self._heating = False                           # стан живе ТУТ, на краю ядра

    def tick(self) -> None:                             # сценарій дверей 1 (цикл)
        reading = self._sensor.read()
        self._heating = decide(reading, self._cfg, self._heating)   # те саме чисте ядро
        self._heater.on() if self._heating else self._heater.off()

    def add_device(self, d: Device) -> None:            # сценарій дверей 2 (CLI/HTTP)
        self._devices.save(d)

    def state(self) -> HomeSnapshot:                    # сценарій дверей 2
        return HomeSnapshot(self._heating, self._devices.all())

    def set_threshold(self, celsius: float) -> None:    # сценарій дверей 2
        self._cfg = replace(self._cfg, threshold=celsius)
