import math
from fractions import Fraction

EULER_MASCHERONI = 0.57721566490153286060

def harmonic_exact_fraction(n: int) -> Fraction:
    """Обчислення точного гармонічного числа як раціонального дробу."""
    if n < 1:
        raise ValueError("n має бути >= 1")
    return sum(Fraction(1, k) for k in range(1, n + 1))

def harmonic_float(n: int) -> float:
    """Гібридне обчислення H[n] з високою точністю."""
    if n < 1:
        raise ValueError("n має бути >= 1")
    
    if n <= 1000:
        # Зворотне підсумовування для збереження точності float
        return sum(1.0 / k for k in range(n, 0, -1))
    
    # Асимптотичний розклад Ейлера — Маклорена
    nd = float(n)
    n2 = nd * nd
    n4 = n2 * n2
    n6 = n4 * n2
    
    return (math.log(nd) + EULER_MASCHERONI 
            + 1.0 / (2.0 * nd) 
            - 1.0 / (12.0 * n2) 
            + 1.0 / (120.0 * n4) 
            - 1.0 / (252.0 * n6))

if __name__ == "__main__":
    print(f"Точний дріб H[5] = {harmonic_exact_fraction(5)}")
    print(f"Float значення H[5] = {float(harmonic_exact_fraction(5))}")
    print(f"H[1_000_000] = {harmonic_float(1_000_000):.15f}")
