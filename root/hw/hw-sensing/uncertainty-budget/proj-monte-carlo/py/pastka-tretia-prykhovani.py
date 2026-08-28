import numpy as np

rng = np.random.default_rng(1)
M = 1_000_000
u1 = u2 = 0.5
r = 0.9
cov = [[u1**2,       r*u1*u2],
       [r*u1*u2,     u2**2  ]]
a, b = rng.multivariate_normal([10.0, 10.0], cov, M).T   # спільна вибірка
y_corr = a + b                                            # чутливості +1, +1

ai = rng.normal(10.0, u1, M)                              # а тепер — незалежно
bi = rng.normal(10.0, u2, M)
y_indep = ai + bi

print(f"якби входи були незалежні:  u = {y_indep.std(ddof=1):.3f}")
print(f"насправді (r = 0.9):        u = {y_corr.std(ddof=1):.3f}")
