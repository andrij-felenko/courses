import math

def block_stats(x):
    """Середнє та стандартне відхилення блоку з n відліків (n > 0).
       Повертає кортеж (mean, sd)."""
    n = len(x)
    total    = 0.0          # сума значень
    total_sq = 0.0          # сума їх квадратів
    for v in x:
        total    += v
        total_sq += v * v   # у Python float — це вже широкий тип (double)
    mean = total / n                        # середнє
    var  = total_sq / n - mean * mean       # середнє кв. − кв. середнього
    if var < 0.0:
        var = 0.0                           # захист від похибки округлення
    return mean, math.sqrt(var)             # корінь повертає одиниці
