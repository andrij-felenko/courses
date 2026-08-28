from dataclasses import dataclass
import math
from functools import reduce
from typing import List

@dataclass(frozen=True)
class Metrics:
    count: int = 0
    sum_val: float = 0.0
    min_val: float = math.inf
    max_val: float = -math.inf
    m2: float = 0.0

    @classmethod
    def empty(cls) -> "Metrics":
        return cls()

    @classmethod
    def from_value(cls, x: float) -> "Metrics":
        return cls(count=1, sum_val=x, min_val=x, max_val=x, m2=0.0)

    def mean(self) -> float:
        return self.sum_val / self.count if self.count > 0 else 0.0

    def combine(self, other: "Metrics") -> "Metrics":
        if self.count == 0:
            return other
        if other.count == 0:
            return self

        total_count = self.count + other.count
        delta = other.mean() - self.mean()
        term = delta * delta * (self.count * other.count / total_count)

        return Metrics(
            count=total_count,
            sum_val=self.sum_val + other.sum_val,
            min_val=min(self.min_val, other.min_val),
            max_val=max(self.max_val, other.max_val),
            m2=self.m2 + other.m2 + term
        )

def parallel_tree_fold(data: List[float]) -> Metrics:
    """Імітація паралельного бінарного дерева редукції."""
    nodes = [Metrics.from_value(x) for x in data]
    if not nodes:
        return Metrics.empty()
    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                next_level.append(nodes[i].combine(nodes[i + 1]))
            else:
                next_level.append(nodes[i])
        nodes = next_level
    return nodes[0]
