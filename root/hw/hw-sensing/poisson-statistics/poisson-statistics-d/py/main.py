from math import sqrt

def poisson_rel_error(counts: int) -> float:
    """Оцінка відносної похибки виміру лічбою за Пуассоном.

    counts — скільки імпульсів (подій) назбирано за час виміру; counts > 0.
    Повертає відносну похибку (частку): 1/√N.
    """
    sigma = sqrt(counts)     # абсолютний розкид ≈ √N
    return sigma / counts    # = 1/√N — відносна похибка


def counts_needed(target: float) -> int:
    """Скільки імпульсів треба назбирати для заданої відносної точності.

    target — бажана відносна похибка (напр. 0.01 для 1 %).
    З 1/√N = target випливає N = 1/target².
    """
    return int(1.0 / (target * target))   # квадратична ціна точності
