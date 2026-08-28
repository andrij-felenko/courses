from dataclasses import dataclass
from collections import Counter, OrderedDict
import random

@dataclass(frozen=True)
class Event:
    t: float        # секунда доступу
    cls: str        # клас даних: registry | twin | telemetry | rights
    key: str        # що читали (ідентифікатор пристрою / дому / гранту)

# Форма кожного класу DH: скільки ключів, наскільки гострий перекіс
# (показник s: більший — вужчий гарячий набір), читань/с і бюджет
# несвіжості в секундах. Бюджет — ЄДИНЕ, чого лог не знає: це політика
# (ворота 3), а не факт, який можна виміряти.
SHAPES = {
    "registry":  dict(keys=5_000,  s=1.1, rps=1000, budget=3600),
    "twin":      dict(keys=5_000,  s=0.7, rps=400,  budget=2),
    "telemetry": dict(keys=2_000,  s=1.0, rps=40,   budget=30),
    "rights":    dict(keys=20_000, s=1.3, rps=200,  budget=0),
}
WINDOW = 600  # секунд у зрізі логу

def zipf_keys(n, s, count, rng):
    # ранг r отримує вагу ≈ 1/rˢ — розподіл, близький до закону Зіпфа
    weights = [1.0 / r**s for r in range(1, n + 1)]
    return rng.choices(range(n), weights=weights, k=count)

def synth_log(rng):
    """Представницький зріз логу DH. Щоб узяти СВІЙ лог, заміни цю
    функцію на читач файлу «t<таб>клас<таб>ключ» — далі все те саме."""
    ev = []
    for cls, sh in SHAPES.items():
        for k in zipf_keys(sh["keys"], sh["s"], sh["rps"] * WINDOW, rng):
            ev.append(Event(rng.random() * WINDOW, cls, f"{cls}:{k}"))
    ev.sort(key=lambda e: e.t)      # лог іде в часовому порядку
    return ev
