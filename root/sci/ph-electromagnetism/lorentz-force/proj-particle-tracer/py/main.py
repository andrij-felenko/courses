import math

class Particle:
    def __init__(self, x, y, z, vx, vy, vz, charge, mass):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.charge = charge
        self.mass = mass

def boris_step(p: Particle, Ex: float, Ey: float, Ez: float,
               Bx: float, By: float, Bz: float, dt: float):
    q_m = p.charge / p.mass
    hdt = 0.5 * dt

    # 1. Половина прискорення E
    v_minus_x = p.vx + q_m * Ex * hdt
    v_minus_y = p.vy + q_m * Ey * hdt
    v_minus_z = p.vz + q_m * Ez * hdt

    # 2. Обертання у магнітному полі B
    tx = q_m * Bx * hdt
    ty = q_m * By * hdt
    tz = q_m * Bz * hdt
    t_sq = tx*tx + ty*ty + tz*tz

    sx = 2.0 * tx / (1.0 + t_sq)
    sy = 2.0 * ty / (1.0 + t_sq)
    sz = 2.0 * tz / (1.0 + t_sq)

    # v' = v_minus + v_minus x t
    v_prime_x = v_minus_x + (v_minus_y * tz - v_minus_z * ty)
    v_prime_y = v_minus_y + (v_minus_z * tx - v_minus_x * tz)
    v_prime_z = v_minus_z + (v_minus_x * ty - v_minus_y * tx)

    # v_plus = v_minus + v' x s
    v_plus_x = v_minus_x + (v_prime_y * sz - v_prime_z * sy)
    v_plus_y = v_minus_y + (v_prime_z * sx - v_prime_x * sz)
    v_plus_z = v_minus_z + (v_prime_x * sy - v_prime_y * sx)

    # 3. Друга половина E
    p.vx = v_plus_x + q_m * Ex * hdt
    p.vy = v_plus_y + q_m * Ey * hdt
    p.vz = v_plus_z + q_m * Ez * hdt

    # 4. Координати
    p.x += p.vx * dt
    p.y += p.vy * dt
    p.z += p.vz * dt

# Тестовий запуск
if __name__ == "__main__":
    e = Particle(0, 0, 0, 1e6, 0, 2e5, -1.602e-19, 9.109e-31)
    dt = 1e-11
    print("Step | X (mm) | Y (mm) | Z (mm)")
    for step in range(1001):
        if step % 200 == 0:
            print(f"{step:4d} | {e.x*1e3:7.3f} | {e.y*1e3:7.3f} | {e.z*1e3:7.3f}")
        boris_step(e, 0, 0, 0, 0, 0, 0.01, dt)
