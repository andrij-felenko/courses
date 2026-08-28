from dataclasses import dataclass

# Один біквад, пряма форма I. Стан — два минулі входи й два минулі виходи.
@dataclass
class Biquad:
    b0: float; b1: float; b2: float   # коефіцієнти прямої гілки (входи)
    a1: float; a2: float              # коефіцієнти зворотної гілки; у формулі віднімаються
    x1: float = 0.0; x2: float = 0.0  # x[n-1], x[n-2]
    y1: float = 0.0; y2: float = 0.0  # y[n-1], y[n-2]

    def step(self, x: float) -> float:
        y = (self.b0 * x  + self.b1 * self.x1 + self.b2 * self.x2
                          - self.a1 * self.y1 - self.a2 * self.y2)   # 5 множень
        # зсуваємо лінії затримки на один такт
        self.x2 = self.x1;  self.x1 = x
        self.y2 = self.y1;  self.y1 = y
        return y
