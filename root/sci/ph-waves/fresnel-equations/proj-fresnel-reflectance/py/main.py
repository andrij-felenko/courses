import cmath
import math

def calculate_fresnel(n1: complex, n2: complex, theta1_deg: float) -> dict:
    theta1_rad = math.radians(theta1_deg)
    cos_t1 = cmath.cos(theta1_rad)
    sin_t1 = cmath.sin(theta1_rad)

    sin_t2 = (n1 / n2) * sin_t1
    cos_t2 = cmath.sqrt(1.0 - sin_t2 ** 2)

    if cos_t2.real < 0.0:
        cos_t2 = -cos_t2

    r_s = (n1 * cos_t1 - n2 * cos_t2) / (n1 * cos_t1 + n2 * cos_t2)
    t_s = (2.0 * n1 * cos_t1) / (n1 * cos_t1 + n2 * cos_t2)

    r_p = (n2 * cos_t1 - n1 * cos_t2) / (n2 * cos_t1 + n1 * cos_t2)
    t_p = (2.0 * n1 * cos_t1) / (n2 * cos_t1 + n1 * cos_t2)

    R_s = abs(r_s) ** 2
    R_p = abs(r_p) ** 2
    R_avg = 0.5 * (R_s + R_p)

    phase_s_deg = math.degrees(cmath.phase(r_s))
    phase_p_deg = math.degrees(cmath.phase(r_p))

    factor = (n2 * cos_t2) / (n1 * cos_t1)
    real_factor = max(0.0, factor.real)

    T_s = real_factor * (abs(t_s) ** 2)
    T_p = real_factor * (abs(t_p) ** 2)

    return {
        "r_s": r_s, "r_p": r_p, "t_s": t_s, "t_p": t_p,
        "R_s": R_s, "R_p": R_p, "T_s": T_s, "T_p": T_p,
        "R_avg": R_avg,
        "phase_s_deg": phase_s_deg, "phase_p_deg": phase_p_deg
    }

if __name__ == "__main__":
    res = calculate_fresnel(1.0, 1.5, 45.0)
    print(f"Повітря -> Скло (45°): R_s={res['R_s']:.4f}, R_p={res['R_p']:.4f}, R_avg={res['R_avg']:.4f}")
