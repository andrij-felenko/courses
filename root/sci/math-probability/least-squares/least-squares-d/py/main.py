# Інкрементна лінійна регресія: y ≈ k·x + b за найменшими квадратами.
# Точки не зберігаємо — лише п'ять накопичувачів.
class Fit:
    def __init__(self):
        self.n = 0              # кількість точок
        self.sx = self.sy = 0.0    # Σx,  Σy
        self.sxx = self.sxy = 0.0  # Σx², Σ(x·y)

    def add(self, x, y):        # згодувати один вимір
        self.n += 1
        self.sx += x;   self.sy += y
        self.sxx += x * x;  self.sxy += x * y

    # Дістати пряму. Повертає (k, b), або None, якщо нахил невизначений
    # (усі x однакові → знаменник нуль, прямої не провести).
    def solve(self):
        den = self.n * self.sxx - self.sx * self.sx   # n·Σx² − (Σx)²
        if den == 0.0:
            return None                                # вертикальна хмара

        k = (self.n * self.sxy - self.sx * self.sy) / den   # нахил
        b = (self.sy - k * self.sx) / self.n                # зсув
        return k, b
