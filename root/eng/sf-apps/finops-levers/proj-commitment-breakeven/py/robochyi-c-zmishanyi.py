from dataclasses import dataclass
from collections.abc import Sequence

# Ставки — мілідолари за машино-годину. Гроші — мілідолари.
@dataclass
class MixPlan:
    committed_md: int    # ставка обіцянки (база)
    spot_md: int         # ставка спота (сплеск)
    retail_md: int       # роздрібна ставка (пік)
    base_level: int      # машин на обіцянці (низ, що завжди ввімкнений)
    spot_cap: int        # стеля спота: усе понад неї йде на роздріб
    period_hours: int    # годин у періоді (для оплати ВСІХ годин обіцянки)


# Внесок кожного тарифу окремо — щоб бачити структуру рахунку, не лише суму.
@dataclass
class MixBill:
    committed_md: int    # за базу: ставка × base_level × ВСІ години періоду
    spot_md: int         # за сплеск: спот-машино-години
    retail_md: int       # за пік: роздрібні машино-години
    total_md: int        # сума трьох


# ── Розкласти профіль по трьох тарифах і порахувати рахунок ──────────────
# demand[h] — скільки машин потрібно на годину h (h = 0..hours-1).
def mixed_bill(demand: Sequence[int], p: MixPlan) -> MixBill:
    # БАЗА оплачується наперед за ВЕСЬ строк, байдуже до погодинного попиту:
    # base_level машин × committed-ставка × усі години періоду.
    committed = p.committed_md * p.base_level * p.period_hours

    # спот покриває від бази до spot_cap; понад spot_cap — роздріб
    spot_ceiling = max(p.spot_cap - p.base_level, 0)

    spot = 0
    retail = 0
    # СПЛЕСК і ПІК рахуємо погодинно — лише за реально спожите понад базу.
    for d in demand:
        if d <= p.base_level:
            continue                        # усе покрила база — понад неї нуль

        above_base = d - p.base_level       # скільки понад базу
        on_spot = min(above_base, spot_ceiling)
        on_retail = above_base - on_spot    # залишок понад стелю спота

        spot += p.spot_md * on_spot         # 1 година кожної машини
        retail += p.retail_md * on_retail

    return MixBill(committed, spot, retail, committed + spot + retail)
