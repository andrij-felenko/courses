import math
from dataclasses import dataclass


@dataclass
class Driver:
    fs: float   # власна частота, Гц
    vas: float  # еквівалентний об'єм, літри
    qts: float  # повна добротність


def sealed_volume_litres(d: Driver, qtc_target: float) -> float:
    """Об'єм закритого ящика під бажану Q_tc.

    Виводиться з V_box = V_as / (α² − 1), де α = Q_tc/Q_ts.
    """
    alpha = qtc_target / d.qts       # у скільки разів піднімаємо Q
    denom = alpha * alpha - 1.0      # α² − 1
    if denom <= 0.0:
        return -1.0                  # Q_tc ≤ Q_ts недосяжна в ЗАКРИТОМУ ящику
    return d.vas / denom


def closed_box_fc(d: Driver, vbox_litres: float) -> float:
    """Частота −3 дБ (для Батерворта Q_tc=0.707 вона дорівнює f_c)."""
    return d.fs * math.sqrt(1.0 + d.vas / vbox_litres)


woofer = Driver(fs=40.0, vas=20.0, qts=0.35)

qtc = 0.707
vbox = sealed_volume_litres(woofer, qtc)
fc = closed_box_fc(woofer, vbox)

print(f"Ціль Q_tc = {qtc:.3f}")
print(f"Об'єм коробки V_box = {vbox:.1f} л")
print(f"Частота в ящику f_c = {fc:.1f} Гц")
