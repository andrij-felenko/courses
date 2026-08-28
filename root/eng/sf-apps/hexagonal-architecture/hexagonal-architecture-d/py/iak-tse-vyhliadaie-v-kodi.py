from abc import ABC, abstractmethod

# ── ПОРТИ (живуть усередині ядра) ──
# Вхідний порт: що ядро ПРОПОНУЄ світу
class ОформленняЗамовлення(ABC):
    @abstractmethod
    async def оформити(self, товари: list[Позиція], пошта: str) -> Замовлення: ...

# Вихідний порт: що ядро ВИМАГАЄ від світу (мовою домену, не SQL)
class ЗамовленняСховище(ABC):
    @abstractmethod
    async def зберегти(self, з: Замовлення) -> None: ...

class Сповіщувач(ABC):
    @abstractmethod
    async def надіслати_підтвердження(self, з: Замовлення) -> None: ...
