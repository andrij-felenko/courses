import time
from dataclasses import dataclass

import pyvisa  # автоматизація стендового вимірювача (DMM + комутатор навантажень)

R1_OHM   = 10.0    # легке навантаження, Ом
R2_OHM   = 2.7     # важче навантаження, Ом
SETTLE_S = 0.05    # пауза на встановлення після перемикання, с
N_AVG    = 32      # скільки відліків усереднити
MIN_DI_A = 0.10    # мінімальна різниця струмів (інакше шум з'їсть знаменник)


class MeasurementError(Exception):
    """Вимір не вдався — точки замалі різні або джерело нелінійне."""


@dataclass
class Norton:
    i_n: float    # струм Нортона (струм КЗ), А — дістаний екстраполяцією
    r_n: float    # опір Нортона (= R_th), Ом
    v_oc: float   # напруга холостого ходу, В — проміжне число


def read_terminal_v(dmm) -> float:
    """Усереднене читання напруги на клемах (у вольтах)."""
    samples = (float(dmm.query("MEAS:VOLT:DC?")) for _ in range(N_AVG))
    return sum(samples) / N_AVG


def measure_point(dmm, load, sel: int, r_ohm: float) -> tuple[float, float]:
    """Зняти одну точку (V, I) під заданим навантаженням."""
    load.select(sel)                    # під'єднати навантаження ключем
    time.sleep(SETTLE_S)                # дочекатися сталого рівня
    v = read_terminal_v(dmm)
    i = v / r_ohm                       # струм точки — навантаження ж відоме
    return v, i


def measure_norton(dmm, load) -> Norton:
    v1, i1 = measure_point(dmm, load, 1, R1_OHM)  # легке навантаження → мала просадка
    v2, i2 = measure_point(dmm, load, 2, R2_OHM)  # важче навантаження → більша просадка
    load.select(0)                      # зняти навантаження — не гріти джерело!

    # запобіжник №1: точки мають давати ДОСИТЬ різні струми,
    # інакше знаменник (i2 − i1) тоне в шумі й R_n стрибає в безглуздя.
    if abs(i2 - i1) < MIN_DI_A:
        raise MeasurementError("I₂−I₁ замале — повторіть з різнішими навантаженнями")

    r_n  = (v1 - v2) / (i2 - i1)        # нахил прямої = внутрішній опір
    v_oc = v1 + i1 * r_n               # екстраполяція вліво, до I = 0

    # запобіжник №2: на справді лінійному джерелі R_n > 0; від'ємний/нуль —
    # ознака грубого збою (переплутані навантаження, шум, нелінійність).
    if r_n <= 0.0:
        raise MeasurementError("R_n ≤ 0 — джерело нелінійне або переплутані навантаження")

    i_n = v_oc / r_n                   # екстраполяція вправо, до V = 0 → струм КЗ
    return Norton(i_n=i_n, r_n=r_n, v_oc=v_oc)


if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    dmm = rm.open_resource("USB0::0x0000::0x0000::INSTR")   # ваш мультиметр
    load = LoadSwitch(rm)                                   # комутатор R1/R2/off
    result = measure_norton(dmm, load)
    print(f"I_n = {result.i_n:.1f} А,  R_n = {result.r_n:.2f} Ом")
