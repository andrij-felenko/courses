def verlet(x, v, h, steps, m=1.0):
    out = [(0.0, x, v, energy(x, v, m))]
    a = -dU(x)/m
    for i in range(steps):
        v_half = v + 0.5*h*a       # пів-удар по швидкості
        x = x + h*v_half           # протяг координати на повний крок
        a = -dU(x)/m               # нова сила в новій точці
        v = v_half + 0.5*h*a       # другий пів-удар
        out.append(((i+1)*h, x, v, energy(x, v, m)))
    return out
