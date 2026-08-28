import math
from collections import defaultdict
from dataclasses import dataclass
from statistics import NormalDist


@dataclass
class Cell:
    """Уся пам'ять, яку коштує зріз: чотири лічильники."""
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0

    @property
    def with_event(self) -> int:      # випадків, де подія БУЛА
        return self.tp + self.fn

    @property
    def without_event(self) -> int:   # де її НЕ було
        return self.fp + self.tn


def accumulate(log) -> dict[str, Cell]:
    """Прохід перший: журнал (зріз, тривога, правда) → лічильники. O(n) часу, O(k) пам'яті."""
    by_slice = defaultdict(Cell)
    for name, alarm, truth in log:
        c = by_slice[name]
        if truth:
            if alarm: c.tp += 1
            else:     c.fn += 1
        else:
            if alarm: c.fp += 1
            else:     c.tn += 1
    return dict(by_slice)


def wilson(k: int, n: int, z: float) -> tuple[float, float]:
    """Інтервал Вілсона: лишається в [0,1] і не схлопується, коли k = 0."""
    if n == 0:
        return 0.0, 1.0
    p, z2 = k / n, z * z
    den = 1.0 + z2 / n
    mid = (p + z2 / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / den
    return max(0.0, mid - half), min(1.0, mid + half)


@dataclass
class Row:
    name: str
    n_without: int
    n_with: int
    far: float                        # частка хибних тривог
    far_ci: tuple[float, float]
    mis: float                        # частка пропусків
    mis_ci: tuple[float, float]


def report(by_slice: dict[str, Cell], min_n: int = 30, alpha: float = 0.05) -> list[Row]:
    """Прохід другий: лічильники → звіт, упорядкований за НИЖНЬОЮ межею."""
    kept = {s: c for s, c in by_slice.items()
            if c.without_event >= min_n or c.with_event >= min_n}
    if not kept:
        return []
    # скільки зрізів переглядаємо — стільки разів маємо шанс «знайти» найгірший
    z = NormalDist().inv_cdf(1 - alpha / (2 * len(kept)))

    rows = [Row(name, c.without_event, c.with_event,
                c.fp / c.without_event if c.without_event else 0.0,
                wilson(c.fp, c.without_event, z),
                c.fn / c.with_event if c.with_event else 0.0,
                wilson(c.fn, c.with_event, z))
            for name, c in kept.items()]
    # угорі — зріз, гірший доведено, а не той, що гірший на вигляд
    return sorted(rows, key=lambda r: -r.far_ci[0])
