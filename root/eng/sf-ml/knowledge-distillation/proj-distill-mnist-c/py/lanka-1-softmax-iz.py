import math

# softmax із температурою: логіти z → ймовірності p.
# T — температура (T=1 звичайний softmax; T>1 м'якший).
# СПЕРШУ віднімаємо max(z/T) — інакше exp() переповнюється й дає inf/nan.
def softmax_T(z, T):
    zt = [zi / T for zi in z]               # логіти, поділені на T
    zmax = max(zt)                          # max уже поділеного на T логіта
    exps = [math.exp(v - zmax) for v in zt] # зсув на max: найбільший показник = 0
    inv = 1.0 / sum(exps)
    return [e * inv for e in exps]          # нормуємо, щоб додавалося в 1
