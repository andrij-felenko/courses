from abc import ABC, abstractmethod
from math import pi

class Shape(ABC):
    @abstractmethod
    def accept(self, v):        # тут починається подвійна диспетчеризація
        ...

class ShapeVisitor(ABC):        # по методу на КОЖЕН вид фігури
    @abstractmethod
    def visit_circle(self, c): ...
    @abstractmethod
    def visit_rectangle(self, r): ...
    @abstractmethod
    def visit_triangle(self, t): ...

class Circle(Shape):
    def __init__(self, r): self.r = r
    def accept(self, v): return v.visit_circle(self)        # я — коло

class Rectangle(Shape):
    def __init__(self, w, h): self.w, self.h = w, h
    def accept(self, v): return v.visit_rectangle(self)

class Triangle(Shape):
    def __init__(self, base, height): self.base, self.height = base, height
    def accept(self, v): return v.visit_triangle(self)
