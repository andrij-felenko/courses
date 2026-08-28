import numpy as np

# Оцінка глибини модуляції з блоку AM-відліків.
# Очікує >= кілька періодів повідомлення у вибірці.
def am_depth(x: np.ndarray) -> float:
    a = np.abs(x)          # |відлік| ≈ миттєва огинаюча
    hi = int(a.max())
    lo = int(a.min())
    if hi + lo == 0:
        return 0.0
    return (hi - lo) / (hi + lo)
