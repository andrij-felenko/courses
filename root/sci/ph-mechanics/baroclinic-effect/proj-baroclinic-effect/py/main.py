import numpy as np

def compute_baroclinic_diagnostics(p, rho, T, dx, dy, dz, f_coriolis=1e-4, g=9.81):
    """
    Обчислює бароклінний момент завихреності та термічний зсув вітру.
    
    Параметри:
      p, rho, T  - 3D масиви форми (Nz, Ny, Nx)
      dx, dy, dz - кроки сітки в метрах
      f_coriolis - параметр Коріоліса (1/с)
      g          - прискорення вільного падіння (м/с²)
    """
    Nz, Ny, Nx = p.shape
    tau_z = np.zeros((Nz, Ny, Nx))
    du_g_dz = np.zeros((Nz, Ny, Nx))
    dv_g_dz = np.zeros((Nz, Ny, Nx))
    
    # Центральні різниці у внутрішніх точках сітки
    dp_dx = np.zeros_like(p)
    dp_dy = np.zeros_like(p)
    drho_dx = np.zeros_like(rho)
    drho_dy = np.zeros_like(rho)
    dT_dx = np.zeros_like(T)
    dT_dy = np.zeros_like(T)
    
    dp_dx[:, 1:-1, 1:-1] = (p[:, 1:-1, 2:] - p[:, 1:-1, :-2]) / (2.0 * dx)
    dp_dy[:, 1:-1, 1:-1] = (p[:, 2:, 1:-1] - p[:, :-2, 1:-1]) / (2.0 * dy)
    
    drho_dx[:, 1:-1, 1:-1] = (rho[:, 1:-1, 2:] - rho[:, 1:-1, :-2]) / (2.0 * dx)
    drho_dy[:, 1:-1, 1:-1] = (rho[:, 2:, 1:-1] - rho[:, :-2, 1:-1]) / (2.0 * dy)
    
    dT_dx[:, 1:-1, 1:-1] = (T[:, 1:-1, 2:] - T[:, 1:-1, :-2]) / (2.0 * dx)
    dT_dy[:, 1:-1, 1:-1] = (T[:, 2:, 1:-1] - T[:, :-2, 1:-1]) / (2.0 * dy)
    
    # Бароклінний момент τ_z = (1/ρ²) * (dρ/dx * dp/dy - dρ/dy * dp/dx)
    rho_sq = rho ** 2
    tau_z = (drho_dx * dp_dy - drho_dy * dp_dx) / rho_sq
    
    # Термічний зсув вітру
    du_g_dz = - (g / (f_coriolis * T)) * dT_dy
    dv_g_dz =   (g / (f_coriolis * T)) * dT_dx
    
    return tau_z, du_g_dz, dv_g_dz
