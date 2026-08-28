from abc import ABC, abstractmethod
from dataclasses import dataclass

class Shape(ABC):                    # завіса: стабільний контракт
    @abstractmethod
    def area(self) -> float: ...

@dataclass
class Circle(Shape):
    r: float
    def area(self) -> float: return 3.14159265 * self.r * self.r

@dataclass
class Rect(Shape):
    w: float
    h: float
    def area(self) -> float: return self.w * self.h

# Нова фігура — НОВИЙ клас, окремий файл. Нічого вище не відкрито:
@dataclass
class Triangle(Shape):
    base: float
    height: float
    def area(self) -> float: return 0.5 * self.base * self.height

def total(shapes: list[Shape]) -> float:   # клієнт закритий
    return sum(s.area() for s in shapes)    # не знає про Triangle
