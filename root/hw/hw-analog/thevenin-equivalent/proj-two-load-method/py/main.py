import time
from dataclasses import dataclass

import pyvisa  # автоматизація стендового вимірювача (DMM + комутатор навантажень)

R1_OHM = 10.0    # легке навантаження, Ом
R2_OHM = 2.7     # важче навантаження, Ом
SETTLE_S = 0.05  # пауза на встановлення після перемикання, с
N_AVG = 16       # скільки відліків усереднити


@dataclass
class Thevenin:
    vth: float
    rth: float


def read_terminal_v(dmm) -> float:
    """Усереднене читання напруги на клемах (у вольтах)."""
    samples = (float(dmm.query("MEAS:VOLT:DC?")) for _ in range(N_AVG))
    return sum(samples) / N_AVG


def measure_thevenin(dmm, load) -> Thevenin:
    load.select(1)                  # легке навантаження
    time.sleep(SETTLE_S)            # дочекатися встановлення
    v1 = read_terminal_v(dmm)
    i1 = v1 / R1_OHM

    load.select(2)                  # важче навантаження
    time.sleep(SETTLE_S)
    v2 = read_terminal_v(dmm)
    i2 = v2 / R2_OHM

    load.select(0)                  # зняти навантаження — не гріти джерело

    rth = (v1 - v2) / (i2 - i1)     # нахил прямої = внутрішній опір
    vth = v1 + i1 * rth             # екстраполяція до I = 0
    return Thevenin(vth, rth)


if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    dmm = rm.open_resource("USB0::0x0000::0x0000::INSTR")   # ваш мультиметр
    load = LoadSwitch(rm)                                   # комутатор R1/R2/off
    result = measure_thevenin(dmm, load)
    print(f"Vth = {result.vth:.2f} В,  Rth = {result.rth:.2f} Ом")
