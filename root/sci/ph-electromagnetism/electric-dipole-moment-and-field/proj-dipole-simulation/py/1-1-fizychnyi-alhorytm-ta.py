import numpy as np

# Фізичні константи SI
EPSILON_0 = 8.8541878128e-12
K_COULOMB = 1.0 / (4.0 * np.pi * EPSILON_0)
DEBYE = 3.33564e-30

def compute_dipole_field_grid(dipole_moment, grid_size=50, box_limit=2e-9):
    """
    Обчислення 3D сітки потенціалу та поля диполя за допомогою векторного NumPy.
    dipole_moment: вектор [px, py, pz] у C*m
    """
    x = np.linspace(-box_limit, box_limit, grid_size)
    y = np.linspace(-box_limit, box_limit, grid_size)
    z = np.linspace(-box_limit, box_limit, grid_size)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Вектор відстані R від центру (0,0,0)
    R_norm = np.sqrt(X**2 + Y**2 + Z**2)
    # Маска для уникнення ділення на нуль у центрі
    mask = R_norm > 1e-12

    Potential = np.zeros_like(R_norm)
    Ex = np.zeros_like(R_norm)
    Ey = np.zeros_like(R_norm)
    Ez = np.zeros_like(R_norm)

    px, py, pz = dipole_moment
    # Скалярний добуток p . r
    p_dot_r = px * X[mask] + py * Y[mask] + pz * Z[mask]

    # Потенціал Phi = (1 / 4pi eps0) * (p . r) / r^3
    Potential[mask] = K_COULOMB * p_dot_r / (R_norm[mask]**3)

    # Вектор поля E = (1 / 4pi eps0) * (3 * (p . r) * r / r^5 - p / r^3)
    coeff_3 = 3.0 * p_dot_r / (R_norm[mask]**5)
    r3 = R_norm[mask]**3

    Ex[mask] = K_COULOMB * (coeff_3 * X[mask] - px / r3)
    Ey[mask] = K_COULOMB * (coeff_3 * Y[mask] - py / r3)
    Ez[mask] = K_COULOMB * (coeff_3 * Z[mask] - pz / r3)

    return X, Y, Z, Potential, Ex, Ey, Ez

if __name__ == "__main__":
    p_h2o = np.array([0.0, 0.0, 1.85 * DEBYE])
    X, Y, Z, Phi, Ex, Ey, Ez = compute_dipole_field_grid(p_h2o)
    print("Сітку поля диполя H2O успішно згенеровано.")
    print(f"Максимальний потенціал на відстані 1 нм: {np.max(np.abs(Phi)):.4f} В")
