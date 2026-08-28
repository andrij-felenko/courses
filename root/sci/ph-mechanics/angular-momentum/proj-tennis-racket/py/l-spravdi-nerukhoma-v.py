def quat_mul(a, b):                       # добуток Гамільтона
    aw, ax, ay, az = a;  bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
    ])

def quat_to_R(q):                         # матриця повороту «тіло → світ»
    w, x, y, z = q
    return np.array([
        [1-2*(y*y+z*z),   2*(x*y-z*w),   2*(x*z+y*w)],
        [  2*(x*y+z*w), 1-2*(x*x+z*z),   2*(y*z-x*w)],
        [  2*(x*z-y*w),   2*(y*z+x*w), 1-2*(x*x+y*y)],
    ])

q = np.array([1.0, 0.0, 0.0, 0.0])        # старт без повороту
for k in range(40_000):                   # 4 секунди
    o = rk4(o, dt)
    q = q + dt * 0.5 * quat_mul(q, np.array([0.0, *o]))
    q = q / np.linalg.norm(q)             # тримаємо кватерніон одиничним
    L_world = quat_to_R(q) @ (I * o)      # момент імпульсу в НЕРУХОМІЙ системі
