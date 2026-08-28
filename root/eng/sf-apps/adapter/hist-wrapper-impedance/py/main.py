from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

S = TypeVar("S"); T = TypeVar("T")

# Один адаптер на БАГАТО джерел: поведінку «як дістати/покласти значення»
# вкладають ЗЗОВНІ — замикачами, а не новим підкласом.
@dataclass
class PluggableAdapter(Generic[S, T]):
    subject: S
    get: Callable[[S], T]
    set: Callable[[S, T], None]
    def value(self) -> T:
        return self.get(self.subject)
    def set_value(self, v: T) -> None:
        self.set(self.subject, v)

# той самий клас пристосовує геть різні об'єкти — без підкласу на кожен:
name_cell = PluggableAdapter(person, lambda p: p.full_name,
                             lambda p, v: setattr(p, "full_name", v))
temp_cell = PluggableAdapter(sensor, lambda s: s.celsius,
                             lambda s, v: setattr(s, "celsius", v))
