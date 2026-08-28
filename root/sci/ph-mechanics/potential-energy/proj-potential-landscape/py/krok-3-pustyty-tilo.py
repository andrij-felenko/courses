def energy(x, v, m=1.0):  return 0.5*m*v*v + U(x)

def euler(x, v, h, steps, m=1.0):
    out = [(0.0, x, v, energy(x, v, m))]
    for i in range(steps):
        a = -dU(x)/m           # прискорення зі СТАРОГО x
        x = x + h*v            # x — за старою швидкістю
        v = v + h*a            # v — за старим прискоренням
        out.append(((i+1)*h, x, v, energy(x, v, m)))
    return out
