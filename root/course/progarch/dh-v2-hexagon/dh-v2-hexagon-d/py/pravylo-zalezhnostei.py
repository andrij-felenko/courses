from dataclasses import dataclass, replace

@dataclass(frozen=True)
class HomeSnapshot:                # DTO: плаский знімок для відповіді назовні
    heating: bool
    devices: list[Device]

class HubService:
    def __init__(self, sensor: Sensor, heater: Heater,
                 devices: DeviceRepository, cfg: Config):
        self._sensor, self._heater = sensor, heater      # драйвовані порти — інтерфейси
        self._devices, self._cfg = devices, cfg
        self._heating = False                            # стан живе тут, на краю ядра

    # ── сценарій, який смикає автономний цикл ──
    def tick(self) -> None:
        reading = self._sensor.read()                    # Sensor: read
        self._heating = decide(reading, self._cfg, self._heating)   # те саме чисте ядро
        self._heater.on() if self._heating else self._heater.off()  # Heater: act

    # ── сценарії, які смикає зовнішній запит (CLI, згодом HTTP) ──
    def add_device(self, d: Device) -> None:
        self._devices.save(d)                            # DeviceRepository

    def state(self) -> HomeSnapshot:
        return HomeSnapshot(self._heating, self._devices.all())

    def set_threshold(self, celsius: float) -> None:
        self._cfg = replace(self._cfg, threshold=celsius)
