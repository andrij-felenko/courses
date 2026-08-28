from dataclasses import dataclass

@dataclass(frozen=True)              # незмінна: споживач не перепише факт по дорозі
class DeviceEvent:                   # опублікована мова стику — лише факт
    device_id: str                  # спільний ідентифікатор (спільне ядро)
    home_id: str
    at: str                         # ISO-час події
    payload: dict                   # {"kind":"state","value":"Locked"}
                                     # | {"kind":"measurement","unit":"°C","value":20.1}
    # жодних вендорських подробиць і жодних живих доменних об'єктів усередині
