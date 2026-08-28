# device_driver.py — АРТЕФАКТ КОНТРАКТУ межі «хаб ↔ драйвер пристрою».
# Обидві сторони імпортують САМЕ цей модуль і спираються лише на нього.
from dataclasses import dataclass
from typing import Literal, Protocol, Union

Celsius = float
Fault = Literal["offline", "timeout"]   # збій межі — лише одне з ЦИХ (множина ЗАКРИТА)

# DTO показу — розрізнене об'єднання: успіх АБО типізований збій-як-значення.
@dataclass(frozen=True)
class Ok:
    temp_c: Celsius
    at: float                # момент зчитування, epoch-СЕКУНДИ

@dataclass(frozen=True)
class Err:
    reason: Fault            # збій — значення, не виняток

Reading = Union[Ok, Err]

# Команда звітує так само — значенням.
@dataclass(frozen=True)
class Accepted: ...

@dataclass(frozen=True)
class Rejected:
    reason: Fault

Ack = Union[Accepted, Rejected]

class DeviceDriver(Protocol):
    def read(self) -> Reading: ...                     # читання заліза
    def set_target(self, temp_c: Celsius) -> Ack: ...  # команда: цільова t°
