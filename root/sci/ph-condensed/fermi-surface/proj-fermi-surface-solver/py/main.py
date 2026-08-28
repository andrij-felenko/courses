import numpy as np

def compute_fermi_surface_properties(t_ev=1.0, a_m=3.0e-10, ef_ev=-1.5, grid_size=500):
    """
    Обчислення площі орбіти та циклотронної маси у 2D сильному зв'язку.
    """
    hbar = 1.054571817e-34
    ev_joule = 1.602176634e-19
    m_e = 9.1093837015e-31
    
    t_j = t_ev * ev_joule
    ef_j = ef_ev * ev_joule
    
    k_max = np.pi / a_m
    kx = np.linspace(-k_max, k_max, grid_size)
    ky = np.linspace(-k_max, k_max, grid_size)
    KX, KY = np.meshgrid(kx, ky)
    
    # Закон дисперсії E(kx, ky)
    E = -2.0 * t_j * (np.cos(KX * a_m) + np.cos(KY * a_m))
    
    # Площа заповнених станів E(k) <= EF
    dk = (2.0 * k_max) / (grid_size - 1)
    area = np.sum(E <= ef_j) * (dk ** 2)
    
    # Мала дельта для похідної dA/dE
    dE = 0.005 * ev_joule
    area_plus = np.sum(E <= (ef_j + dE)) * (dk ** 2)
    area_minus = np.sum(E <= (ef_j - dE)) * (dk ** 2)
    
    dA_dE = (area_plus - area_minus) / (2.0 * dE)
    m_c = (hbar ** 2 / (2.0 * np.pi)) * dA_dE
    
    return area, m_c, m_c / m_e

if __name__ == "__main__":
    area, m_c, m_ratio = compute_fermi_surface_properties(ef_ev=-1.5)
    print(f"Площа орбіти в k-просторі: {area:.4e} м⁻²")
    print(f"Циклотронна маса m_c*: {m_c:.4e} кг ({m_ratio:.3f} m_e)")
