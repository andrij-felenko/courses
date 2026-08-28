import bisect
import math
from dataclasses import dataclass, field
from statistics import NormalDist


@dataclass
class Binning:
    """Границі бінів — рівночастотні квантилі НАВЧАЛЬНОЇ вибірки. Заморожені назавжди."""
    edges: list[float] = field(default_factory=list)

    @classmethod
    def fit(cls, train: list[float], bins: int) -> "Binning":
        s = sorted(train)
        raw = [s[len(s) * i // bins] for i in range(1, bins)]
        return cls(sorted(set(raw)))   # однакові межі = порожній бін уже на навчанні

    @property
    def bins(self) -> int:
        return len(self.edges) + 1

    def histogram(self, xs) -> list[int]:
        h = [0] * self.bins
        for x in xs:                   # O(n log B) на весь потік
            h[bisect.bisect_right(self.edges, x)] += 1
        return h


def shares(h: list[int]) -> list[float]:
    """Півдодавання Джеффріса: (xᵢ + ½)/(N + B/2) — нуль перестає давати ln(0)."""
    total, B = sum(h), len(h)
    return [(c + 0.5) / (total + 0.5 * B) for c in h]


def psi(p: list[float], q: list[float]) -> float:
    """PSI = Σ (pᵢ − qᵢ)·(ln pᵢ − ln qᵢ)."""
    return sum((pi - qi) * (math.log(pi) - math.log(qi)) for pi, qi in zip(p, q))


def psi_alarm(n: int, m: int, bins: int, alpha: float = 0.05) -> float:
    """Межа тривоги замість сталих 0.10 і 0.25."""
    df = bins - 1
    return (1 / n + 1 / m) * (df + NormalDist().inv_cdf(1 - alpha) * math.sqrt(2 * df))
