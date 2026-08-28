from dataclasses import dataclass
from enum import Enum, auto

class NumberClass(Enum):
    DEFICIENT = auto()
    PERFECT = auto()
    ABUNDANT = auto()

@dataclass(frozen=True)
class AbundanceResult:
    number: int
    sigma: int
    sum_proper: int
    index: float
    classification: NumberClass

class AbundanceAnalyzer:
    @staticmethod
    def analyze(n: int) -> AbundanceResult:
        if n <= 0:
            raise ValueError("Number must be positive")
        if n == 1:
            return AbundanceResult(1, 1, 0, 1.0, NumberClass.DEFICIENT)

        temp = n
        current_sigma = 1
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                term_sum = 1
                p_power = 1
                while temp % d == 0:
                    p_power *= d
                    term_sum += p_power
                    temp //= d
                current_sigma *= term_sum
            d += 1

        if temp > 1:
            current_sigma *= (1 + temp)

        sum_proper = current_sigma - n
        idx = current_sigma / n

        if sum_proper == n:
            cls = NumberClass.PERFECT
        elif sum_proper > n:
            cls = NumberClass.ABUNDANT
        else:
            cls = NumberClass.DEFICIENT

        return AbundanceResult(n, current_sigma, sum_proper, idx, cls)
