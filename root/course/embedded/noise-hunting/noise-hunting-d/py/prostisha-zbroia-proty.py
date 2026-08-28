import math


# Загороджувальний біквадрат: глушить рівно f0, лишає решту спектра.
# f0 — частота гулу (50 Гц), fs — частота дискретизації, Q — гострота
# вирізу (більше Q → вужчий, глибший провал саме на 50 Гц).
class Notch:
    def __init__(self, f0, fs, Q):
        w0 = 2.0 * math.pi * f0 / fs
        c, s = math.cos(w0), math.sin(w0)
        alpha = s / (2.0 * Q)
        a0 = 1.0 + alpha                # нормувальник
        self.b0 =  1.0      / a0        # коефіцієнти вирізу:
        self.b1 = -2.0 * c  / a0        # чисельник має нулі точно на f0,
        self.b2 =  1.0      / a0        # тому саме ця частота гаситься в нуль
        self.a1 = -2.0 * c  / a0
        self.a2 = (1.0 - alpha) / a0
        self.x1 = self.x2 = self.y1 = self.y2 = 0.0

    # Пряма форма II transposed — по одному відліку за виклик.
    def step(self, x):
        y = (self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2
                         - self.a1 * self.y1 - self.a2 * self.y2)
        self.x2, self.x1 = self.x1, x
        self.y2, self.y1 = self.y1, y
        return y
