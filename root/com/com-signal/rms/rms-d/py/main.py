import math

def block_rms(x):
    """Діюче (RMS) значення блоку з відліків.
    x — виміряні відліки сигналу; має бути непорожнім."""
    sum_sq = 0.0
    for xi in x:
        sum_sq += xi * xi           # крок 1: квадрат, і одразу в суму
    mean_sq = sum_sq / len(x)       # крок 2: середнє квадрата
    return math.sqrt(mean_sq)       # крок 3: корінь повертає одиниці
