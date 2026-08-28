import math

# Один такт pure pursuit. Вхід: позиція (px,py), курс theta [рад], швидкість v.
# Вихід: кут керма delta [рад]. Коли шлях завершено — ставить pp.finished
# і повертає 0 (кермо прямо).
def pursuit_step(pp, px, py, theta, v):
    if pp.finished:
        return 0.0

    # 1) випередження, пропорційне швидкості, з нижньою межею
    L = max(pp.k_look * v, pp.L_min)

    # 2) знайти ціль-точку
    c = (px, py)
    goal = pursuit_find_goal(pp, c, L)
    if goal is None:
        return 0.0                              # шлях завершено

    # 3) бічний зсув цілі в системі апарата (поворот на −theta)
    dx = goal[0] - px
    dy = goal[1] - py
    s, co = math.sin(theta), math.cos(theta)
    x_lat = -s * dx + co * dy                   # бічна координата цілі

    # 4) кривина дуги pure pursuit; L беремо як фактичну відстань до цілі
    l_real = math.hypot(dx, dy)                 # справжня відстань апарат→ціль
    if l_real < 1e-3:
        return 0.0                              # ціль злилась з апаратом — прямо
    kappa = 2.0 * x_lat / (l_real * l_real)

    # 5) переклад у кут керма (велосипедна модель) + затиск межами
    delta = math.atan(pp.wheelbase * kappa)
    return max(-pp.delta_max, min(pp.delta_max, delta))
