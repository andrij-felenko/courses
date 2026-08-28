import math, random

def predict(x, p, v, dt, q):
    return x + v*dt, p + q                 # прокрутити модель, роздути p

def correct(x, p, z, r):
    K = p / (p + r)                        # відносна певність, 0..1
    return x + K*(z - x), (1 - K)*p, K     # підтягти x, звузити p

dt, v, q, r = 1.0, 1.0, 0.25, 9.0          # ДИСПЕРСІЇ q, r (а не σ!)
sig_proc, sig_meas, N = 0.5, 3.0, 100
random.seed(1)

x_true, x, p, x_dead = 0.0, -20.0, 100.0, -20.0   # навмисне хибний старт
se_t = se_r = se_d = 0.0
for k in range(1, N + 1):
    x_true += v*dt + random.gauss(0, sig_proc)     # істина: швидкість + поштовхи
    z = x_true + random.gauss(0, sig_meas)         # зашумлений вимір

    x, p = predict(x, p, v, dt, q)                 # ← передбач
    x, p, K = correct(x, p, z, r)                  # ← виправ
    x_dead += v*dt                                 # прогноз без корекцій дрейфує

    se_t += (x      - x_true)**2
    se_r += (z      - x_true)**2
    se_d += (x_dead - x_true)**2
    if k <= 6:
        print(f"k={k}  K={K:.3f}  p={p:.3f}")

rms = lambda s: math.sqrt(s / N)
print(f"RMS: трекер={rms(se_t):.2f}  вимір={rms(se_r):.2f}  прогноз={rms(se_d):.2f} (м)")
