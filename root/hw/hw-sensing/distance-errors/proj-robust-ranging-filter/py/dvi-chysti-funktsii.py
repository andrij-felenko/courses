# median3 = середній з трьох.
def median3(a: int, b: int, c: int) -> int:
    return sorted((a, b, c))[1]


# Сила відлуння → довіра [0..1]: лінійно між підлогою й стелею.
def confidence(s: int, floor: int, full: int) -> float:
    if s <= floor:
        return 0.0
    if s >= full:
        return 1.0
    return (s - floor) / (full - floor)
