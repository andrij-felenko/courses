from dataclasses import dataclass

@dataclass
class ABCD:
    A: float; B: float; C: float; D: float

def abcd_mul(m1, m2):     # m1 — перша за сигналом ланка
    return ABCD(
        m1.A * m2.A + m1.B * m2.C,
        m1.A * m2.B + m1.B * m2.D,
        m1.C * m2.A + m1.D * m2.C,
        m1.C * m2.B + m1.D * m2.D,
    )

# Цеглинки з бібліотеки:
def series_z(Z): return ABCD(1.0, Z,   0.0, 1.0)   # {1,Z,0,1}
def shunt_y(Y):  return ABCD(1.0, 0.0, Y,   1.0)   # {1,0,Y,1}

# Перевірка взаємності: для пасивної ланки має бути AD − BC ≈ 1.
def reciprocity(m): return m.A * m.D - m.B * m.C
