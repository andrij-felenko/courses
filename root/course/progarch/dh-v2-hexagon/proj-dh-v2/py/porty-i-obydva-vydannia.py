# ── Порти: застосунок залежить від них, а не від марки заліза ──
class Sensor(Protocol):
    def read(self) -> Reading: ...

class Heater(Protocol):
    def on(self) -> None: ...        # ідемпотентно
    def off(self) -> None: ...

class DeviceRepository(Protocol):
    def save(self, d: Device) -> None: ...
    def all(self) -> list[Device]: ...

# ── Справжні адаптери: єдині, хто говорить мовою заліза ──
class OneWireThermometer:            # реалізує Sensor: DS18B20 по 1-Wire
    def __init__(self, w1_id: str):
        self._path = f"/sys/bus/w1/devices/{w1_id}/w1_slave"
    def read(self) -> Reading:
        try:
            text = open(self._path).read()          # "...crc=.. YES\n.. t=20125"
            milli = int(text.split("t=")[-1])       # DS18B20 віддає мілі-градуси
            return Reading(celsius=milli / 1000, ok=True)   # переклад одиниць ТУТ, на краю
        except (OSError, ValueError):
            return Reading(celsius=float("nan"), ok=False)  # німий давач → «не вірю»

class SmartPlug:                     # реалізує Heater: Wi-Fi розетка (напр. Shelly)
    def __init__(self, url: str):
        self._url, self._on = url, False
    def on(self) -> None:
        if not self._on: self._toggle("on");  self._on = True
    def off(self) -> None:
        if self._on:     self._toggle("off"); self._on = False
    def _toggle(self, turn: str) -> None:
        import urllib.request
        urllib.request.urlopen(f"{self._url}/relay/0?turn={turn}", timeout=3)

# ── Підробки: кожен порт має свою, дім живе в пам'яті ──
class FakeSensor:                    # реалізує Sensor: віддає задану температуру
    def __init__(self, celsius: float = 18.0):
        self.celsius, self.ok = celsius, True   # тест крутить ці поля, граючи сценарій
    def read(self) -> Reading:
        return Reading(self.celsius, self.ok)

class FakeHeater:                    # реалізує Heater: журнал перемикань, без реле
    def __init__(self):
        self._on = False
        self.log: list[bool] = []
    def on(self) -> None:
        if not self._on: self._on = True;  self.log.append(True)   # лише реальні зміни
    def off(self) -> None:
        if self._on:     self._on = False; self.log.append(False)

class InMemoryDeviceRepository:      # реалізує DeviceRepository: реєстр у пам'яті
    def __init__(self):
        self._items: list[Device] = []
    def save(self, d: Device) -> None:
        self._items.append(d)
    def all(self) -> list[Device]:
        return list(self._items)
