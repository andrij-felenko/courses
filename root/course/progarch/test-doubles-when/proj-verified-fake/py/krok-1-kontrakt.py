from dataclasses import dataclass
from typing import Protocol

@dataclass
class Reading:
    at: int          # epoch, мс
    celsius: float

# Контракт сховища. Дві реалізації нижче обіцяють РІВНО це — й нічого понад.
class ReadingStore(Protocol):
    def save(self, r: Reading) -> None: ...
    def recent(self, limit: int) -> list[Reading]: ...   # до limit найсвіжіших; найсвіжіше — перше
