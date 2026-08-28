import random, bisect
from dataclasses import dataclass

@dataclass
class Factor:
    name: str
    lo: float          # нижній кінець діапазону
    nom: float         # найімовірніше (номінал)
    hi: float          # верхній кінець
    unit: str = ""

# ── модель: піковий трафік (запитів/с) як добуток припущень ──
def peak_rps(v):
    daily = v["DAU"] * v["sessions"] * v["actions"] * v["req"]   # запитів на добу
    return daily * v["peak_frac"] / 3600.0                        # у пікову секунду

FACTORS = [
    Factor("DAU",       180_000, 200_000, 220_000, "корист./добу"),
    Factor("sessions",      2.5,     3.0,     3.5, "сеансів/корист."),
    Factor("actions",        15,      20,      25, "дій/сеанс"),
    Factor("req",             4,       4,       4, "запитів/дію"),
    Factor("peak_frac",    0.05,    0.10,    0.30, "частка в пік. годину"),
]
THRESHOLD = 2000.0    # запитів/с — стеля одного сервера
