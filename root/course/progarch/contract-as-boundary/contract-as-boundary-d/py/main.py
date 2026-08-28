from dataclasses import dataclass
from typing import Protocol, Literal, Union

Celsius = float

@dataclass(frozen=True)
class Ok:
    temp_c: Celsius
    at: float                       # час зчитування, epoch-секунди

@dataclass(frozen=True)
class Err:
    reason: Literal["offline", "timeout"]   # збій — значення, не виняток

Reading = Union[Ok, Err]

class DeviceDriver(Protocol):
    # ПЕРЕДУМОВА: не частіше ніж раз на секунду.
    # ПОСТУМОВА:  Ok(temp_c у [-40, 85]) або Err; НЕ кидає винятку крізь межу.
    def read(self) -> Reading: ...
