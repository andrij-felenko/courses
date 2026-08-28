from dataclasses import dataclass, field
from enum import Enum, auto


@dataclass
class Sample:
    dist_mm: int = 0     # виміряна відстань, мм
    strength: int = 0    # сила відлуння (напр. 0..1023); 0 = нема луни
    t_ms: int = 0        # мітка часу САМОГО виміру, мс
    valid: bool = False  # чи відлуння взагалі прийшло


class RangeStatus(Enum):
    FRESH = auto()   # свіжий достовірний вимір
    HELD  = auto()   # тримаємо старе (короткий пропуск або відкинутий стрибок)
    LOST  = auto()   # надто довго наосліп — відстань НЕВІДОМА (для уникання = небезпека)


@dataclass
class RangeResult:
    status: RangeStatus
    mm: int = 0         # згладжена за довірою оцінка
    med_mm: int = 0     # гейтований медіан — крайо-зберігаючий, для безпекових рішень
    conf: float = 0.0   # довіра до цього виміру, 0..1


@dataclass
class RangeFilter:
    vmax_mm_s: int              # найгірша швидкість ЗБЛИЖЕННЯ, мм/с
    floor: int                  # нижче — dropout
    full: int                   # вище — повна довіра

    ring: list = field(default_factory=lambda: [0, 0, 0])  # кільцевий буфер для медіани-3
    head: int = 0               # куди писати
    fill: int = 0               # скільки вже лягло (0..3)

    last_mm: int = 0            # останнє ПРИЙНЯТЕ значення — опора воріт
    last_ms: int = 0
    have_last: bool = False

    est: float = 0.0            # згладжена оцінка
    have_est: bool = False

    margin_mm: int = 15         # запас воріт на шум самого виміру
    base_alpha: float = 0.6     # базова жвавість злиття при повній довірі
    max_drops: int = 3          # скільки пропусків поспіль тримати старе, тоді LOST
    max_rejects: int = 4        # скільки «неможливих» стрибків поспіль терпіти, тоді пере-захопити
    drops: int = 0
    rejects: int = 0            # поточні лічильники
