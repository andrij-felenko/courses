from bisect import bisect_left

def nearest(sorted_e, x):
    """Найближче до x значення у відсортованій таблиці ряду (двійковий пошук)."""
    i = bisect_left(sorted_e, x)
    if i == 0:
        return sorted_e[0]
    if i == len(sorted_e):
        return sorted_e[-1]
    lo, hi = sorted_e[i - 1], sorted_e[i]
    return hi if hi - x < x - lo else lo

def find_pair(target, e_series):
    """target = бажане R1/R2 = (1−k)/k з потрібного виходу.
       e_series — усі значення E24 по декадах (відсортовані)."""
    best, best_err = None, float("inf")
    for r2 in e_series:
        r1_ideal = target * r2
        r1 = nearest(e_series, r1_ideal)              # двійковий пошук
        err = abs(r1 - target * r2) / (target * r2)   # відносна похибка (без ділення R1/R2)
        if err < best_err:
            best_err, best = err, (r1, r2)
    return best, best_err
