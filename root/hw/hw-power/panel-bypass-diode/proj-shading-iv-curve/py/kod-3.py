def local_maxima(P):
    """Індекси локальних максимумів P(V), злиті в межах 0.5 А один від одного."""
    peaks = []
    for i in range(1, len(P) - 1):
        if P[i] >= P[i-1] and P[i] > P[i+1]:
            if peaks and I[i] - I[peaks[-1]] < 0.5:
                if P[i] > P[peaks[-1]]:
                    peaks[-1] = i
            else:
                peaks.append(i)
    return peaks

def hill_climb(P, start=1):
    """Perturb-and-observe: з робочої точки повземо туди, де потужність росте,
    поки не впремося в локальний максимум. Старт — біля холостого ходу."""
    i = start
    while 0 < i < len(P) - 1:
        if   P[i+1] > P[i]: i += 1
        elif P[i-1] > P[i]: i -= 1
        else: break
    return i
