import numpy as np

def start(y0, v0, r2, dt, left="fixed", right="fixed"):
    """Другий стан із форми й швидкості: схемі потрібні ДВА, а фізика дає інше."""
    cur = y0 + dt*v0
    cur[1:-1] += 0.5*r2*(y0[:-2] - 2.0*y0[1:-1] + y0[2:])          # ПОЛОВИННА поправка
    cur[0]  = 0.0 if left  == "fixed" else cur[0]  + r2*(y0[1]  - y0[0])
    cur[-1] = 0.0 if right == "fixed" else cur[-1] + r2*(y0[-2] - y0[-1])
    return cur

def step(prev, cur, nxt, r2, left="fixed", right="fixed"):
    """Один крок за часом; буфери повертаються крутнутими по колу."""
    nxt[1:-1] = 2.0*cur[1:-1] - prev[1:-1] + r2*(cur[:-2] - 2.0*cur[1:-1] + cur[2:])
    # закріплений край стоїть; вільний бачить дзеркального сусіда: y[−1] = y[1]
    nxt[0]  = 0.0 if left  == "fixed" else 2.0*cur[0]  - prev[0]  + 2.0*r2*(cur[1]  - cur[0])
    nxt[-1] = 0.0 if right == "fixed" else 2.0*cur[-1] - prev[-1] + 2.0*r2*(cur[-2] - cur[-1])
    return cur, nxt, prev        # prev←cur, cur←щойно пораховане, nxt←звільнений буфер

c, L, N = 400.0, 0.65, 200       # м/с, м, число проміжків
dx = L / N                       # 3.25 мм
r  = 0.9                         # число Куранта, r ≤ 1 (див. далі)
dt = r * dx / c                  # 7.31 мкс
r2 = r * r

x = np.linspace(0.0, L, N + 1)
xp, h = 0.2*L, 0.003             # защип: 1/5 довжини, висота 3 мм
y0 = np.where(x < xp, h*x/xp, h*(L - x)/(L - xp))
y0[0] = y0[-1] = 0.0
v0 = np.zeros_like(y0)           # відпускаємо без поштовху

prev = y0
cur  = start(y0, v0, r2, dt)
nxt  = np.empty_like(y0)

for n in range(int(0.01 / dt)):  # 10 мс звучання
    prev, cur, nxt = step(prev, cur, nxt, r2)
    print("%.6f %+.6e" % ((n + 1)*dt, cur[N // 7]))     # «знімач» під струною
