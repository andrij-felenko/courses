def step_euler(s, dt):
    x, y, vx, vy = s
    ax, ay = accel(x, y)
    s[0], s[1] = x + vx*dt,  y + vy*dt        # положення рухаємо СТАРОЮ швидкістю
    s[2], s[3] = vx + ax*dt, vy + ay*dt       # швидкість — старим прискоренням

def run(step, dt, nsteps, s0=(1.0, 0.0, 0.0, 1.2)):
    s = list(s0)
    E0 = energy(*s); emin = emax = E0
    for _ in range(nsteps):
        step(s, dt)
        e = energy(*s)
        emin, emax = min(emin, e), max(emax, e)
    return s, (emax - emin) / abs(E0)          # розмах енергії відносно початкової
