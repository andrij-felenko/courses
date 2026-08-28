import numpy as np
from scipy.special import digamma, polygamma, zeta

# Константа Ейлера — Маскероні в SciPy
EULER_GAMMA = 0.57721566490153286060

def harmonic_scipy(x):
    """Векторизоване обчислення H[x] для масивів NumPy або чисел."""
    return digamma(np.asarray(x) + 1.0) + EULER_GAMMA

# Приклад обчислення для масиву аргументів
arr = np.array([1, 2, 5, 10, 100])
print("H[arr] =", harmonic_scipy(arr))

# Узагальнене гармонічне число H[n, m] через дзета-функцію Гурвіца
def harmonic_generalized_scipy(n, m):
    return zeta(m, 1) - zeta(m, n + 1)

print("H[10, 2] =", harmonic_generalized_scipy(10, 2))
