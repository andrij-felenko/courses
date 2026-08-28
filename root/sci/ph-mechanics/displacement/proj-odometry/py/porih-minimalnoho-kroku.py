def path_length_deadband(pts: list[Point], eps: float) -> float:
    """Шлях із порогом кроку. Відрізок зараховуємо лише коли відхід
    від ОСТАННЬОЇ ЗБЕРЕЖЕНОЇ точки (якоря) досяг eps."""
    if not pts:
        return 0.0
    total = 0.0
    ax, ay = pts[0]                    # якір — остання збережена точка
    for x, y in pts[1:]:
        step = math.hypot(x - ax, y - ay)
        if step >= eps:
            total += step
            ax, ay = x, y              # якір рухаємо ЛИШЕ на зарахованому кроці
    return total
