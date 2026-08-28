# демо-мова: прозоро, стан — простий список
def accel(x, y):
    inv = -GM / (x*x + y*y)**1.5              # −GM / r³
    return inv*x, inv*y

def verlet_step(s, dt):
    x, y, vx, vy = s
    ax, ay = accel(x, y)
    x += vx*dt + 0.5*ax*dt*dt                 # дрейф
    y += vy*dt + 0.5*ay*dt*dt
    ax2, ay2 = accel(x, y)                    # сила в новій точці
    s[0], s[1] = x, y
    s[2] = vx + 0.5*(ax + ax2)*dt             # швидкість — середнім прискоренням
    s[3] = vy + 0.5*(ay + ay2)*dt

s = [1.0, 0.0, 0.0, 1.2]
for _ in range(100_000_000):                  # сто мільйонів кроків — і енергія не тікає
    verlet_step(s, 0.01)
