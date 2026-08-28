import math

g = 9.81                                    # м/с², тяжіння вниз

def accel(state, k):
    """Похідна стану. k = c/m — коефіцієнт квадратичного опору (1/м)."""
    x, y, vx, vy = state
    speed = math.hypot(vx, vy)              # |v| — саме воно зчіплює осі
    ax = -k * speed * vx                     # опір проти горизонтального руху
    ay = -g - k * speed * vy                 # тяжіння + опір проти вертикального
    return (vx, vy, ax, ay)                  # (ẋ, ẏ, v̇ₓ, v̇_y)

def rk4_step(state, k, dt):
    add = lambda s, d, h: tuple(si + h*di for si, di in zip(s, d))
    k1 = accel(state, k)                      # нахил на старті
    k2 = accel(add(state, k1, dt/2), k)       # …на пробному півкроці
    k3 = accel(add(state, k2, dt/2), k)       # …ще раз посередині
    k4 = accel(add(state, k3, dt), k)         # …у кінці кроку
    return tuple(s + dt/6*(a + 2*b + 2*c + d)  # зважене середнє чотирьох
                 for s, a, b, c, d in zip(state, k1, k2, k3, k4))
