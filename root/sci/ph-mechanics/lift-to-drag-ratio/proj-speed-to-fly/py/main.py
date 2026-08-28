from dataclasses import dataclass
from math import pi, sqrt

@dataclass
class Glider:
    m: float          # маса, кг
    S: float          # площа крила, м²
    b: float          # розмах, м
    CD0: float        # паразитний опір за нульового підйому
    e: float          # коефіцієнт Освальда
    rho: float = 1.225   # густина повітря, кг/м³
    g: float = 9.81

    @property
    def W(self):   return self.m * self.g            # вага, Н
    @property
    def Lam(self): return self.b**2 / self.S         # видовження Λ
    @property
    def k(self):   return 1.0 / (pi * self.e * self.Lam)   # множник індуктивного опору

    def CD(self, CL):                                # поляра опору одним рядком
        return self.CD0 + self.k * CL**2

    @property
    def CL_best(self):                               # CL максимальної якості: індукт. = паразит.
        return sqrt(self.CD0 / self.k)
    @property
    def LD_max(self):
        return 1.0 / (2.0 * sqrt(self.CD0 * self.k))

    def speed(self, CL):                             # швидкість для даного CL (пологе планування, L≈W)
        return sqrt(2.0 * self.W / (self.rho * self.S * CL))

    @property
    def V_bg(self):                                  # швидкість найкращого планування
        return self.speed(self.CL_best)

    @property
    def CL_minsink(self):                            # мінімальне зниження: індукт. = 3·паразит.
        return sqrt(3.0) * self.CL_best
    @property
    def V_ms(self):
        return self.speed(self.CL_minsink)

    def sink(self, V):                               # вертикальна швидкість зниження на швидкості V
        CL = 2.0 * self.W / (self.rho * V*V * self.S)
        return V * self.CD(CL) / CL                  # = V / (L/D)

    def reach(self, h, headwind=0.0):                # проста дальність із висоти з поправкою на вітер
        return self.LD_max * h * (1.0 - headwind / self.V_bg)

    def speed_to_fly(self, headwind=0.0):            # оптимальна швидкість проти вітру
        # максимізуємо (V − вітер)/sink(V) — дотична з точки (вітер, 0) до поляри
        best_V, best_gr = self.V_bg, -1.0
        V = self.V_ms * 0.7
        while V < self.V_bg * 2.2:
            gr = (V - headwind) / self.sink(V)
            if gr > best_gr:
                best_gr, best_V = gr, V
            V += 0.02
        return best_V, best_gr                       # швидкість (м/с) і якість над землею
