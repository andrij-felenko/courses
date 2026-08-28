# Грубозернистий інтерфейс: один виклик — один перехід через межу.
# Повертає не об'єкти з поведінкою, а пласкі пакунки даних.
@dataclass
class DeviceDTO:                     # самі поля, жодного методу
    type: str; room: str; state: str
    brightness: int; last_seen: float

class Dashboard(Protocol):
    async def snapshot(self) -> list[DeviceDTO]: ...   # усі 30 за один похід

all_devices = await dashboard.snapshot()    # 1 перехід через межу
for d in all_devices:
    render(d.type, d.room, d.state, d.brightness, d.last_seen)
