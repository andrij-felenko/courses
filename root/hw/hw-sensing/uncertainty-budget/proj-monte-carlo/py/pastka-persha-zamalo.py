import numpy as np

for M in (200, 2_000, 20_000, 200_000):
    us, q95 = [], []
    for k in range(30):
        rr = np.random.default_rng(1000 + k)
        L = rr.uniform(0.949, 0.951, M)
        T = rr.normal(97.77, 0.25, M) / 50
        g = 4 * np.pi**2 * L / T**2
        us.append(g.std(ddof=1))
        q95.append(np.percentile(g, 97.5))
    print(f"M = {M:>7}:  u гуляє на {max(us)-min(us):.4f},  "
          f"край 97.5 % гуляє на {max(q95)-min(q95):.4f}")
