import math
from dataclasses import dataclass

TWO_PI = 2.0 * math.pi


@dataclass
class Tia:
    Rf: float       # резистор перетворення, Ом
    Cin: float      # повна вхідна ємність (діод + ОП + монтаж), Ф
    f_gbw: float    # добуток підсилення на смугу ОП, Гц
    Cf: float = 0.0  # конденсатор компенсації, Ф


# Частоти зламів коефіцієнта зворотного зв'язку
def fz_of(t: Tia) -> float:                   # нуль 1/β від вхідної ємності
    return 1.0 / (TWO_PI * t.Rf * (t.Cin + t.Cf))


def fp_of(t: Tia) -> float:                   # полюс 1/β від Cf = смуга −3 дБ
    return 1.0 / (TWO_PI * t.Rf * t.Cf)


# |A|·β = 1: ОП з одним домінантним полюсом має |A(f)| ≈ f_gbw / f.
# 1/β(f) на полиці прямує до (Cin+Cf)/Cf; точну криву беремо з полюса й нуля.
def crossover_hz(t: Tia) -> float:
    fz, fp = fz_of(t), fp_of(t)
    # |A(f)| = f_gbw/f;  |1/β(f)| = sqrt(1+(f/fz)^2) / sqrt(1+(f/fp)^2)
    # шукаємо f, де f_gbw/f = |1/β|, простим діленням навпіл по логарифму
    lo, hi = fp * 0.05, t.f_gbw               # перетин гарантовано в цьому вікні
    for _ in range(60):
        f = math.sqrt(lo * hi)                # середина в лог-масштабі
        A = t.f_gbw / f
        ib = math.sqrt(1.0 + (f/fz)**2) / math.sqrt(1.0 + (f/fp)**2)
        if A > ib:                            # |A| ще вище за 1/β → перетин правіше
            lo = f
        else:
            hi = f
    return math.sqrt(lo * hi)


# Запас фази (градуси) при поточному Cf
def phase_margin_deg(t: Tia) -> float:
    fz, fp, fc = fz_of(t), fp_of(t), crossover_hz(t)
    # фаза петлі: −90° (полюс ОП) − atan(fc/fz) (нуль 1/β) + atan(fc/fp) (полюс 1/β)
    phase = -90.0 - math.degrees(math.atan(fc/fz)) + math.degrees(math.atan(fc/fp))
    return 180.0 + phase                      # запас до −180°


# Cf-орієнтир максимально плоского відгуку (полюс у геом. середині fz та f_gbw)
def cf_butterworth(Rf: float, Cin: float, f_gbw: float) -> float:
    return math.sqrt(Cin / (TWO_PI * Rf * f_gbw))


# Приклад: Rf = 1 МОм, Cin = 60 пФ, f_gbw = 10 МГц
def check_example() -> None:
    t = Tia(Rf=1.0e6, Cin=60.0e-12, f_gbw=10.0e6)
    t.Cf = cf_butterworth(t.Rf, t.Cin, t.f_gbw)   # ≈ 0.98 пФ
    pm = phase_margin_deg(t)                       # ≈ 45° — мінімально безпечно
    bw = fp_of(t)                                  # смуга −3 дБ ≈ 162 кГц
    if pm < 45.0:
        pass  # запас замалий: побільшити Cf (нижчий полюс) або взяти швидший ОП
    _ = (pm, bw)
