from dataclasses import dataclass

@dataclass
class Abr:
    rate: int             # поточний цільовий бітрейт, біт/с
    rate_min: int         # підлога: нижче не опускаємось (гірша допустима якість)
    rate_max: int         # стеля: вище не піднімаємось (краща потрібна якість)

    # пороги втрат у ПРОМІЛЕ (‰), щоб лишитись у цілій арифметиці:
    #   20‰ = 2%   (поріг росту),   100‰ = 10%  (поріг падіння)
    loss_up_permille: int = 20      # < цього → рости    (2.0%)
    loss_down_permille: int = 100   # > цього → падати   (10.0%)

    up_step_pct: int = 5            # крок угору, % (наприклад, 5 → ×1.05)


def abr_init(start: int, lo: int, hi: int) -> Abr:
    return Abr(rate=start, rate_min=lo, rate_max=hi)
