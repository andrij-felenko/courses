import math
from dataclasses import dataclass
from typing import Callable, Optional

Curve = Callable[[float], float]   # P(схибив) як функція тижнів розвідки

def exp_decay(p0: float, t_cal: float, p_cal: float) -> Curve:
    """P(t) = p0·e^(−t/τ); сталу τ підганяємо так, щоб P(t_cal) = p_cal."""
    tau = -t_cal / math.log(p_cal / p0)          # з p_cal = p0·e^(−t_cal/τ)
    return lambda t: p0 * math.exp(-t / tau)

@dataclass
class Trade:
    delay_week: float      # вартість зволікання, €/тиждень
    fix_cost: float        # ціна виправлення, €
    p_wrong: Curve         # P(схибив) від тижнів чекання

@dataclass
class Game:
    weeks: float           # скільки тижнів коштує сам хід «зміни гру» (скелет)
    fix_cost: float        # у скільки впаде ціна виправлення за інтерфейсом
    p_wrong: float         # P(схибив) на пізнішому, вимірянному рішенні

def total_cost(t: float, tr: Trade) -> float:
    """Сумарна очікувана вартість плану «чекати t тижнів, тоді вирішувати»."""
    return tr.delay_week * t + tr.p_wrong(t) * tr.fix_cost

def optimal_wait(tr: Trade, t_max: float = 24.0, step: float = 0.01) -> tuple[float, float]:
    """Дно U-кривої = останній відповідальний момент. Скан — щоб годився
    будь-який спад P, не лише експонента (для неї є й формула, як перевірка)."""
    best_t, best_c = 0.0, total_cost(0.0, tr)
    for i in range(1, int(t_max / step) + 1):
        t = i * step
        c = total_cost(t, tr)
        if c < best_c:
            best_t, best_c = t, c
    return best_t, best_c

def recommend(tr: Trade, game: Optional[Game] = None, weak: float = 0.05):
    now = total_cost(0.0, tr)
    t_star, c_star = optimal_wait(tr)
    plans = [("вирішити зараз", 0.0, now),
             (f"чекати до LRM (t*={t_star:.2f} тиж)", t_star, c_star)]
    if game is not None:
        g = tr.delay_week * game.weeks + game.p_wrong * game.fix_cost
        plans.append(("змінити гру", game.weeks, g))
    name, wk, cost = min(plans, key=lambda p: p[2])
    thin = (now - c_star) < weak * now      # дно ледь нижче за «вирішити зараз»?
    return name, cost, plans, {"t_star": t_star, "saving": now - c_star, "thin": thin}

# ── Digital Homes: де зберігати телеметрію ──────────────────────────────────
dh = Trade(delay_week=4000, fix_cost=60000,
           p_wrong=exp_decay(p0=0.5, t_cal=6, p_cal=0.2))   # зараз монетка; за 6 тиж → 0.2
game = Game(weeks=1, fix_cost=8000, p_wrong=0.15)           # скелет+інтерфейс здешевлюють усе

name, cost, plans, diag = recommend(dh, game)

print("Digital Homes — телеметрія: чекати чи вирішувати?\n")
for label, wk, c in plans + [("чекати 6 тиж (наївно)", 6.0, total_cost(6.0, dh))]:
    print(f"  {label:32}{wk:5.1f} тиж   {c:8.0f} €")
print(f"\n  ПРИПИС: {name.upper()}  →  {cost:.0f} €")
if diag["thin"]:
    print(f"  timing-важіль слабкий: оптимальне чекання економить лише "
          f"{diag['saving']:.0f} € — дно U-кривої майже впритул до «вирішити зараз».")
    print("  зволікання й помилка дорогі водночас → шукай структурний хід.")
