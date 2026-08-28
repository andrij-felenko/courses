from enum import Enum
from dataclasses import dataclass

class LockState(Enum):          # замкнений перелік: жодного стану поза цими чотирма
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    JAMMED = "jammed"
    UNKNOWN = "unknown"         # чесний стан «хаб не чув від замка», не None і не діра

@dataclass(frozen=True)         # frozen → незмінний + рівність за вмістом задарма
class DeviceId:
    value: str
