# domain/tariff.py — НАШ світ. Мова доставки. Про HTTP не чув.
from dataclasses import dataclass

@dataclass(frozen=True)
class Напрямок:
    код: str          # "SEG_A", "SEG_B" — наш ключ напрямку

@dataclass(frozen=True)
class Тариф:
    одиниць: float    # уже наше число, не rate_bps
    def дорожчий_за(self, поріг: float) -> bool:
        return self.одиниць > поріг

# Доменні помилки: НАШІ поняття біди. У них перекладуться чужі коди.
class ТарифНедоступний(Exception):
    def __init__(self, напрямок: Напрямок):
        self.напрямок = напрямок
        super().__init__(f"Тарифу для напрямку {напрямок.код} немає")

class ДоступПрострочено(Exception):
    def __init__(self):
        super().__init__("Доступ до служби тарифів прострочено")

class ШлюзНедоступний(Exception):     # сервіс зламався або не відповів
    def __init__(self, причина: str):
        self.причина = причина
        super().__init__(f"Служба тарифів недоступна: {причина}")
