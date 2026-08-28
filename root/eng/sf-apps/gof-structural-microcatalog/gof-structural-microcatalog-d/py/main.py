from abc import ABC, abstractmethod

# Реалізація: ЯК фізично намалювати примітив (вісь 1)
class Renderer(ABC):
    @abstractmethod
    def draw_circle(self, x, y, r): ...

class VectorRenderer(Renderer):
    def draw_circle(self, x, y, r):
        return f"<circle cx={x} cy={y} r={r}/>"        # SVG

class RasterRenderer(Renderer):
    def draw_circle(self, x, y, r):
        return f"піксельне коло R={r} у ({x},{y})"      # растр

# Абстракція: ЩО малюємо; тримає рушій і делегує (вісь 2)
class Shape(ABC):
    def __init__(self, renderer: Renderer):
        self.r = renderer                 # ← міст до реалізації
    @abstractmethod
    def draw(self): ...

class Circle(Shape):
    def __init__(self, renderer, x, y, rad):
        super().__init__(renderer)
        self.x, self.y, self.rad = x, y, rad
    def draw(self):
        return self.r.draw_circle(self.x, self.y, self.rad)

c = Circle(VectorRenderer(), 10, 10, 5)
print(c.draw())      # <circle .../>  — векторний
# той самий Circle з іншим рушієм: жодного нового класу
print(Circle(RasterRenderer(), 10, 10, 5).draw())
