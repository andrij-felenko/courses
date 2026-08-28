def flight(v0, angle_deg, k, dt=0.005):
    """Кинути під кутом, крокувати до землі; повернути (дальність, вершина, кут падіння)."""
    a = math.radians(angle_deg)
    s = (0.0, 0.0, v0*math.cos(a), v0*math.sin(a))     # старт із початку координат
    apex = 0.0
    while True:
        nxt = rk4_step(s, k, dt)
        apex = max(apex, nxt[1])                        # найвища точка дорогою
        if nxt[1] <= 0.0 < nxt[0]:                      # перетнули землю всередині кроку
            frac = s[1] / (s[1] - nxt[1])               # частка кроку до y = 0
            xr = s[0] + frac*(nxt[0] - s[0])            # інтерполюємо дальність
            vx = s[2] + frac*(nxt[2] - s[2])
            vy = s[3] + frac*(nxt[3] - s[3])
            return xr, apex, math.degrees(math.atan2(-vy, vx))  # +кут удару об землю
        s = nxt
