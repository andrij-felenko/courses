import math
from dataclasses import dataclass

@dataclass
class Amp:
    name:   str
    vos25:  float   # В: зсув напруги, паспортний МАКСИМУМ за 25 °C
    tcvos:  float   # В/°C: максимальний дрейф зсуву напруги
    ib25:   float   # А: середній вхідний струм, максимум за 25 °C
    ios25:  float   # А: струм неузгодженості, максимум за 25 °C
    t_flat: float   # °C: доки струм сталий; вище — подвоєння на кожні 10 °C

@dataclass
class Circuit:
    r_plus:     float          # Ом: опір постійному струмові з «плюс»-входу
    r_minus:    float          # Ом: те саме з «мінус»-входу
    noise_gain: float = 1.0    # у стільки разів похибка входу росте на виході
    swing:      float = 10.0   # В: скільки вихід може відійти від робочої точки

@dataclass
class Error:
    vos:   float    # знімається калібруванням самого приладу
    cur:   float    # знімається лише разом із датчиком
    drift: float    # не знімається нічим — межа точності

    def total(self):
        return self.vos + self.cur + self.drift


def bias_at(a: Amp, t: float):
    """Струми входу за температури t: витік подвоюється кожні 10 °C вище t_flat."""
    over = t - a.t_flat
    k = 1.0 if over <= 0.0 else 2.0 ** (over / 10.0)
    return a.ib25 * k, a.ios25 * k


def dc_error(a: Amp, c: Circuit, t: float) -> Error:
    """Похибка, зведена до входу. Знаки доданків наперед невідомі,
    тож найгірший випадок — сума модулів."""
    ib, ios = bias_at(a, t)
    dr = abs(c.r_plus - c.r_minus)   # різниця опорів — на неї діє I_B
    sr = c.r_plus + c.r_minus        # сума опорів    — на неї діє I_os
    return Error(vos=a.vos25,
                 cur=a.ib25 * dr + 0.5 * a.ios25 * sr,
                 drift=(a.tcvos * abs(t - 25.0)
                        + (ib - a.ib25) * dr
                        + 0.5 * (ios - a.ios25) * sr))


def worst_case(a: Amp, c: Circuit, tmin: float, tmax: float) -> Error:
    """Найгірше по діапазону. Кожен доданок опуклий за t (модуль і показникова),
    а максимум опуклої функції на відрізку — на його кінці. Тож двох точок досить."""
    return max((dc_error(a, c, t) for t in (tmin, tmax)), key=Error.total)
