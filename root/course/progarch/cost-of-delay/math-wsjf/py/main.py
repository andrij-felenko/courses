from dataclasses import dataclass

@dataclass
class Decision:
    name: str
    cod: float          # вартість зволікання, €/тиждень
    dur: float          # тривалість розбору, тижнів

def waiting_cost(order: list[Decision]) -> float:
    """Сумарна зважена вартість очікування Σ CoD_j · C_j."""
    week, total = 0.0, 0.0
    for d in order:
        week += d.dur                 # тиждень готовності цього рішення
        total += d.cod * week         # усе зволікання, що набігло до нього
    return total

def wsjf_order(ds: list[Decision]) -> list[Decision]:
    # спадання відношення CoD/тривалість — правило Сміта
    return sorted(ds, key=lambda d: d.cod / d.dur, reverse=True)

board = [
    Decision("телеметрія",     4000, 2),
    Decision("автентифікація", 1500, 1),
    Decision("білінг",         6000, 6),
]

best = wsjf_order(board)
loud = sorted(board, key=lambda d: d.cod, reverse=True)   # спершу найбільша CoD

print([d.name for d in best], waiting_cost(best))   # …, 66500.0
print([d.name for d in loud], waiting_cost(loud))   # …, 81500.0
