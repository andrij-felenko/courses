# domain/order.py — НАШ світ. Мова складу. Про CRM не чув.
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Article: code: str

@dataclass(frozen=True)
class Color:
    name: str
    @staticmethod
    def parse(s: str) -> "Color": return Color(s)

@dataclass(frozen=True)
class Size:
    label: str
    @staticmethod
    def parse(s: str) -> "Size": return Size(s)

@dataclass(frozen=True)
class ClientId: value: str

@dataclass(frozen=True)
class Product:
    article: Article
    color: Color
    size: Size

@dataclass(frozen=True)
class Order:
    client: ClientId
    product: Product
    quantity: int  # завжди > 0 — модель від'ємних не знає
    def reserve(self) -> None: ...  # чисте доменне правило складу

# Порт: що домен ВИМАГАЄ. Оголошено нашою мовою.
class OrderSource(ABC):
    @abstractmethod
    def next(self) -> Order | None: ...
