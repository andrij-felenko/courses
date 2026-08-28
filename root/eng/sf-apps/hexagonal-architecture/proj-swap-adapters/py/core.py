# order/core.py ── ЯДРО. Не імпортує НІЧОГО зовнішнього.
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Позиція:
    товар: str
    ціна: int
    кількість: int


@dataclass(frozen=True)
class Замовлення:
    id: str
    пошта: str
    позиції: tuple[Позиція, ...]

    @staticmethod
    def створити(id: str, пошта: str, позиції: list[Позиція]) -> "Замовлення":
        if not позиції:
            raise ValueError("порожнє замовлення")          # ПРАВИЛО
        if "@" not in пошта:
            raise ValueError("недійсна пошта")              # ПРАВИЛО
        return Замовлення(id, пошта, tuple(позиції))

    def сума(self) -> int:
        return sum(п.ціна * п.кількість for п in self.позиції)   # ПРАВИЛО


# ── ПОРТИ ──
# Вхідний: що ядро ПРОПОНУЄ світу
class ОформленняЗамовлення(ABC):
    @abstractmethod
    async def оформити(self, пошта: str, позиції: list[Позиція]) -> Замовлення: ...


# Вихідний: що ядро ВИМАГАЄ від світу — рівно два дієслова, мовою домену
class ЗамовленняСховище(ABC):
    @abstractmethod
    async def зберегти(self, з: Замовлення) -> None: ...
    @abstractmethod
    async def узяти(self, id: str) -> Замовлення | None: ...
