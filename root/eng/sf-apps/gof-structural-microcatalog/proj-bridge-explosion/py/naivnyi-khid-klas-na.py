import math

# НАЇВНО: клас на КОЖНУ пару «фігура × рушій»
class SvgStar:
    def __init__(self, cx, cy, outer, inner, n=5):
        self.cx, self.cy, self.outer, self.inner, self.n = cx, cy, outer, inner, n
    def draw(self, out):
        pts = []
        for i in range(self.n * 2):                        # ← математика зірки, копія №1
            rad = self.outer if i % 2 == 0 else self.inner
            t = math.pi * i / self.n - math.pi / 2         # −π/2, щоб вістря дивилось угору
            pts.append((self.cx + rad * math.cos(t), self.cy + rad * math.sin(t)))
        d = " ".join("%.1f,%.1f" % p for p in pts)
        out.append('<polygon points="%s" fill="none" stroke="black"/>' % d)

class AsciiStar:
    def __init__(self, cx, cy, outer, inner, n=5):
        self.cx, self.cy, self.outer, self.inner, self.n = cx, cy, outer, inner, n
    def draw(self, grid):
        pts = []
        for i in range(self.n * 2):                        # ← ТА САМА математика, копія №2
            rad = self.outer if i % 2 == 0 else self.inner
            t = math.pi * i / self.n - math.pi / 2
            pts.append((self.cx + rad * math.cos(t), self.cy + rad * math.sin(t)))
        for a, b in zip(pts, pts[1:] + [pts[0]]):
            plot_segment(grid, a, b)

# class StatsStar:  ← копія №3, з тим самим циклом і тим самим −π/2
