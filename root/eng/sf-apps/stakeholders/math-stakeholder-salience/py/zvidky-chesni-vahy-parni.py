from math import prod

def reciprocal(n, upper):
    M = [[1.0] * n for _ in range(n)]
    for (i, j), v in upper.items():
        M[i][j], M[j][i] = v, 1.0 / v
    return M

def ahp(M):
    n = len(M)
    gm = [prod(M[i]) ** (1 / n) for i in range(n)]     # середнє геометричне рядка
    s = sum(gm)
    w = [g / s for g in gm]                             # нормовані ваги
    Aw = [sum(M[i][j] * w[j] for j in range(n)) for i in range(n)]
    lam = sum(Aw[i] / w[i] for i in range(n)) / n       # оцінка λmax
    CI = (lam - n) / (n - 1)
    RI = {3: 0.58, 4: 0.90, 5: 1.12}[n]
    return w, lam, CI / RI

labels = ["вартість", "доступність", "швидкодія", "безпека"]

# Розсудлива матриця: вартість трохи важливіша за решту, безпека ≈ доступність.
sane = reciprocal(4, {(0, 1): 2, (0, 2): 3, (0, 3): 2, (1, 2): 2, (1, 3): 1, (2, 3): 0.5})
# Матриця з циклом: 0>1, 1>2, але 2>0 (у скільки разів «i важливіший» іде по колу).
cyclic = reciprocal(4, {(0, 1): 2, (1, 2): 2, (0, 2): 0.5, (0, 3): 1, (1, 3): 1, (2, 3): 1})

for name, M in (("розсудлива", sane), ("з циклом", cyclic)):
    w, lam, CR = ahp(M)
    print(f"{name}:  ваги = " + ", ".join(f"{l} {round(100*x)}%" for l, x in zip(labels, w)))
    verdict = "узгоджено" if CR <= 0.10 else "НЕУЗГОДЖЕНО — перегляньте судження"
    print(f"           λmax = {lam:.3f},  CR = {CR:.3f}  → {verdict}\n")
