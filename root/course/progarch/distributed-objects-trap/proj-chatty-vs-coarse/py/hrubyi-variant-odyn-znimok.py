from dataclasses import dataclass

# Плаский пакунок: самі поля, нуль поведінки, версія формату. Скроєний на дріт.
@dataclass
class DeviceDTO:
    v: int
    id: str
    type: str; room: str; state: str
    brightness: int; last_seen: float

class Hub:
    # ... register / get / ids — як вище ...

    # ГРУБА межа: один метод збирає ВЕСЬ реєстр у пакунок.
    # Усі геттери тут дарові — Device лежить у тому самому процесі.
    def snapshot(self):
        return [DeviceDTO(1, d.id, d.type(), d.room(), d.state(),
                          d.brightness(), d.last_seen())
                for d in self._devices.values()]
