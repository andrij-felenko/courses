def euler(dt, T):
    x, y, vx, vy = 0.0, 0.0, v, 0.0
    for _ in range(round(T/dt)):
        ax = omega**2 * x + 2*omega*vy
        ay = omega**2 * y - 2*omega*vx
        x, y = x + vx*dt, y + vy*dt          # положення — за старою швидкістю
        vx, vy = vx + ax*dt, vy + ay*dt      # швидкість — за старим прискоренням
    return x, y

for dt in (0.1, 0.02):
    x, y = euler(dt, T)
    print(f"dt = {dt}:  ({x:+.3f}, {y:+.3f})   r = {np.hypot(x, y):.2f}")
