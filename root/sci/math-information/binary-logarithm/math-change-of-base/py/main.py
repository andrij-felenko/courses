import math

# ✗ Перехід між основами просто в коді.
#   Увага: math.log(n, 2) — це те саме ділення всередині, з тією ж вадою
def log2_via_ln(n: int) -> float:
    return math.log(n) / math.log(2)
# n = 2**29 → 29.000000000000004 → math.ceil(…) → 30, зайвий біт

# ✓ Виділена функція: ділення немає
def log2_direct(n: int) -> float:
    return math.log2(n)
# n = 2**29 → рівно 29.0 → math.ceil(…) → 29
