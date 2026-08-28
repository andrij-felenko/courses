import numpy as np

# Фундаментальні фізичні сталі у системі SI
G = 6.67430e-11          # Гравітаційна стала, m^3 kg^-1 s^-2
C = 2.99792458e8         # Швидкість світла, m/s
M_SUN = 1.98847e30       # Маса Сонця, kg
M_E = 9.1093837e-31      # Маса електрона, kg
M_U = 1.660539066e-27    # Атомна одиниця маси, kg
HBAR = 1.054571817e-34   # Зведена стала Планка, J s

# Параметри речовини білого карлика (вуглець/кисень, mu_e = 2.0)
MU_E = 2.0
B_CONST = (8.0 * np.pi * (M_E * C)**3 * MU_E * M_U) / (3.0 * (2.0 * np.pi * HBAR)**3)  # kg/m^3
A_CONST = (np.pi * M_E**4 * C**5) / (3.0 * (2.0 * np.pi * HBAR)**3)                     # Pa

def eos_density(x):
    """Обчислює масову густину rho(x) за імпульсом Фермі x."""
    return B_CONST * (x**3)

def eos_pressure(x):
    """Точний релятивістський тиск Чандрасекара P(x)."""
    if x < 1e-4:
        return (8.0 / 15.0) * A_CONST * (x**5)
    return A_CONST * (x * (2.0 * x**2 - 3.0) * np.sqrt(1.0 + x**2) + 3.0 * np.arcsinh(x))

def inv_eos_x(p_target):
    """Знаходить безрозмірний імпульс x за заданим тиском P методом Ньютона."""
    if p_target <= 0:
        return 0.0
    x = (15.0 * p_target / (8.0 * A_CONST))**0.2
    for _ in range(25):
        p_val = eos_pressure(x)
        dp_dx = 8.0 * A_CONST * (x**4) / np.sqrt(1.0 + x**2)
        diff = p_val - p_target
        if abs(diff) < 1e-9 * p_target:
            break
        x -= diff / dp_dx
        if x < 0:
            x = 1e-10
    return x

def solve_white_dwarf(rho_center, dr=500.0):
    """
    Чисельно інтегрує рівняння рівноваги від центра до поверхні.
    Повертає масу (в одиницях M_sun) та радіус (в кілометрах).
    """
    x_center = (rho_center / B_CONST)**(1.0 / 3.0)
    p_center = eos_pressure(x_center)
    
    r = dr
    m = (4.0 / 3.0) * np.pi * (r**3) * rho_center
    p = p_center - (2.0 / 3.0) * np.pi * G * (rho_center**2) * (r**2)
    
    while p > 1e-7 * p_center and r < 5e7:
        def derivatives(r_val, m_val, p_val):
            if p_val <= 0:
                return 0.0, 0.0
            x_val = inv_eos_x(p_val)
            rho_val = eos_density(x_val)
            dp_dr = - (G * m_val * rho_val) / (r_val**2)
            dm_dr = 4.0 * np.pi * (r_val**2) * rho_val
            return dm_dr, dp_dr

        dm1, dp1 = derivatives(r, m, p)
        dm2, dp2 = derivatives(r + 0.5 * dr, m + 0.5 * dr * dm1, p + 0.5 * dr * dp1)
        dm3, dp3 = derivatives(r + 0.5 * dr, m + 0.5 * dr * dm2, p + 0.5 * dr * dp2)
        dm4, dp4 = derivatives(r + dr, m + dr * dm3, p + dr * dp3)

        m += (dr / 6.0) * (dm1 + 2.0 * dm2 + 2.0 * dm3 + dm4)
        p += (dr / 6.0) * (dp1 + 2.0 * dp2 + 2.0 * dp3 + dp4)
        r += dr

    return m / M_SUN, r / 1000.0

if __name__ == "__main__":
    densities = [1e8, 1e9, 1e10, 1e11, 1e12, 1e13]  # kg/m^3
    print(f"{'Центральна густина (г/см³)':>28} | {'Маса (M_☉)':>10} | {'Радіус (км)':>11}")
    print("-" * 57)
    for rho_c in densities:
        m_star, r_star = solve_white_dwarf(rho_c)
        print(f"{(rho_c / 1000.0):28.1e} | {m_star:10.3f} | {r_star:11.1f}")
