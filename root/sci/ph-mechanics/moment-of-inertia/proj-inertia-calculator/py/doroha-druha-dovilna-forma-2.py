import random

def disc_inertia_mc(R, M, n):
    """Той самий момент інерції методом Монте-Карло: кидаємо n випадкових
    точок у квадрат 2R×2R, лишаємо ті, що впали в диск; кожне влучання —
    рівний шматок маси M/влучань. Похибка спадає як 1/√n."""
    s = 0.0
    inside = 0
    for _ in range(n):
        x = random.uniform(-R, R)
        y = random.uniform(-R, R)
        if x*x + y*y <= R*R:
            s += x*x + y*y
            inside += 1
    return s * (M / inside)
