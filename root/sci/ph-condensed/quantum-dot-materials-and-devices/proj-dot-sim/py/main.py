import math

def calculate_brus_gap(r_nm, e_g0=1.74, m_e=0.13, m_h=0.45, eps_r=9.3):
    """
    Обчислює заборонену зону E_g(R) [еВ] за рівнянням Брюса.
    r_nm — радіус точки у нанометрах.
    """
    if r_nm <= 0.2:
        return e_g0
    conf_coeff = 3.73  # eV * nm^2
    coul_coeff = 0.276 # eV * nm
    return e_g0 + conf_coeff / (r_nm ** 2) - coul_coeff / r_nm

def simulate_pl_spectrum(r_mean, sigma_r, num_points=100):
    """
    Генерує спектр фотолюмінесценції ансамблю квантових точок.
    """
    wavelengths = []
    intensities = []
    
    lambda_start, lambda_end = 400.0, 750.0
    step = (lambda_end - lambda_start) / (num_points - 1)
    
    for i in range(num_points):
        wl = lambda_start + i * step
        energy_ev = 1239.84 / wl  # E = hc / λ
        
        intensity = 0.0
        for j in range(-30, 31):
            r_step = r_mean + j * 0.01
            if r_step <= 0.3:
                continue
            e_g = calculate_brus_gap(r_step)
            prob = (1.0 / (sigma_r * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((r_step - r_mean) / sigma_r) ** 2)
            gamma = 0.03 # еВ однорідне уширення
            line_shape = (gamma / (2 * math.pi)) / ((energy_ev - e_g)**2 + (gamma / 2)**2)
            intensity += prob * line_shape
            
        wavelengths.append(wl)
        intensities.append(intensity)
        
    return wavelengths, intensities

def coulomb_blockade_current(v_bias, v_gate, r_nm, temp_k=4.2):
    """
    Обчислює тунельний струм [нА] у режимі кулонівської облокади.
    """
    e_charge = 1.602e-19
    k_b = 8.617e-5 # eV/K
    eps_0 = 8.854e-12
    eps_r = 9.3
    
    r_m = r_nm * 1e-9
    c_tot = 4 * math.pi * eps_0 * eps_r * r_m
    u_c = (e_charge / (2 * c_tot)) / e_charge # в еВ
    
    gate_alpha = 0.5
    energy_level = u_c - gate_alpha * v_gate
    
    k_t = k_b * temp_k
    f_source = 1.0 / (1.0 + math.exp((energy_level - v_bias / 2.0) / k_t))
    f_drain  = 1.0 / (1.0 + math.exp((energy_level + v_bias / 2.0) / k_t))
    
    g0_nanoamps = 100.0
    current = g0_nanoamps * (f_source - f_drain)
    return current, u_c

if __name__ == "__main__":
    r_mean = 3.0 # нм
    sigma = 0.15 # нм
    wl, pl = simulate_pl_spectrum(r_mean, sigma, num_points=10)
    print(f"Спектр PL для R = {r_mean} нм (пік при λ ≈ {wl[pl.index(max(pl))]:.1f} нм)")
    
    current, u_c = coulomb_blockade_current(v_bias=0.01, v_gate=0.2, r_nm=2.5, temp_k=4.2)
    print(f"Кулонівська енергія U_C = {u_c*1000:.2f} меВ, струм I = {current:.3f} нА")
