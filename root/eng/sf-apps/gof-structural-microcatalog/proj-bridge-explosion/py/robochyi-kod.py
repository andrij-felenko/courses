import math
from abc import ABC, abstractmethod

# ── Реалізація: ЯК виводимо (вісь 1) ──────────────────────────
class Renderer(ABC):
    @abstractmethod
    def begin(self, w, h): ...
    @abstractmethod
    def polyline(self, pts, closed): ...
    @abstractmethod
    def ellipse(self, cx, cy, rx, ry): ...
    @abstractmethod
    def end(self): ...


class SvgRenderer(Renderer):
    def begin(self, w, h):
        self.out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (w, h)]
    def polyline(self, pts, closed):
        d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        tag = "polygon" if closed else "polyline"
        self.out.append('  <%s points="%s" fill="none" stroke="black"/>' % (tag, d))
    def ellipse(self, cx, cy, rx, ry):
        self.out.append('  <ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" '
                        'fill="none" stroke="black"/>' % (cx, cy, rx, ry))
    def end(self):
        self.out.append("</svg>")
        return "\n".join(self.out)


class AsciiRenderer(Renderer):
    def begin(self, w, h):
        self.w, self.h = w, h
        self.g = [[" "] * w for _ in range(h)]
    def _plot(self, x, y):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < self.w and 0 <= yi < self.h:
            self.g[yi][xi] = "#"
    def _segment(self, a, b):
        (x1, y1), (x2, y2) = a, b
        steps = max(int(abs(x2 - x1)), int(abs(y2 - y1)), 1) * 2
        for i in range(steps + 1):
            t = i / steps
            self._plot(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
    def polyline(self, pts, closed):
        seq = (pts + [pts[0]]) if closed else pts
        for a, b in zip(seq, seq[1:]):
            self._segment(a, b)
    def ellipse(self, cx, cy, rx, ry):
        steps = max(8, int(4 * (rx + ry)))
        for i in range(steps):
            t = 2 * math.pi * i / steps
            self._plot(cx + rx * math.cos(t), cy + ry * math.sin(t))
    def end(self):
        return "\n".join("".join(row).rstrip() for row in self.g)


class StatsRenderer(Renderer):
    def begin(self, w, h):
        self.n = 0
        self.box = None
    def _grow(self, x, y):
        if self.box is None:
            self.box = [x, y, x, y]
        else:
            self.box[0] = min(self.box[0], x); self.box[1] = min(self.box[1], y)
            self.box[2] = max(self.box[2], x); self.box[3] = max(self.box[3], y)
    def polyline(self, pts, closed):
        self.n += 1
        for x, y in pts:
            self._grow(x, y)
    def ellipse(self, cx, cy, rx, ry):
        self.n += 1
        self._grow(cx - rx, cy - ry); self._grow(cx + rx, cy + ry)
    def end(self):
        x1, y1, x2, y2 = self.box
        return "примітивів: %d; рамка: (%.1f,%.1f)–(%.1f,%.1f)" % (self.n, x1, y1, x2, y2)
