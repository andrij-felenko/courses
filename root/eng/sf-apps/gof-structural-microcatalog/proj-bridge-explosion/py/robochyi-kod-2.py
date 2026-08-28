# ── Абстракція: ЩО малюємо (вісь 2) ───────────────────────────
class Shape(ABC):
    def __init__(self, r):
        self.r = r                       # ← МІСТ до реалізації
    @abstractmethod
    def draw(self): ...


class Circle(Shape):
    def __init__(self, r, cx, cy, rad):
        super().__init__(r); self.cx, self.cy, self.rad = cx, cy, rad
    def draw(self):
        self.r.ellipse(self.cx, self.cy, self.rad, self.rad)


class Rect(Shape):
    def __init__(self, r, x, y, w, h):
        super().__init__(r); self.x, self.y, self.w, self.h = x, y, w, h
    def draw(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.r.polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True)


class Triangle(Shape):
    def __init__(self, r, a, b, c):
        super().__init__(r); self.pts = [a, b, c]
    def draw(self):
        self.r.polyline(self.pts, True)


class Star(Shape):
    def __init__(self, r, cx, cy, outer, inner, points=5):
        super().__init__(r)
        self.cx, self.cy, self.outer, self.inner, self.points = cx, cy, outer, inner, points
    def draw(self):
        pts = []
        for i in range(self.points * 2):
            rad = self.outer if i % 2 == 0 else self.inner
            t = math.pi * i / self.points - math.pi / 2
            pts.append((self.cx + rad * math.cos(t), self.cy + rad * math.sin(t)))
        self.r.polyline(pts, True)       # геометрія зірки — ОДИН раз на всі рушії


class Scene:
    def __init__(self, r, shapes):
        self.shapes = shapes
        self.use(r)
    def use(self, r):                    # ← жива заміна рушія на льоту
        self.r = r
        for s in self.shapes:
            s.r = r
    def draw(self, w, h):
        self.r.begin(w, h)
        for s in self.shapes:
            s.draw()
        return self.r.end()
