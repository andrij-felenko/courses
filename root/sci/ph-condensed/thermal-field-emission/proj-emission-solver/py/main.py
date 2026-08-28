import numpy as np
import matplotlib.pyplot as plt

# Фізичні константи
e = 1.602176634e-19
m = 9.1093837015e-31
h = 6.62607015e-34
k_B = 1.380649e-23
eps0 = 8.8541878128e-12

A_0 = (4.0 * np.pi * m * e * k_B**2) / (h**3)
A_FN = (e**3) / (8.0 * np.pi * h)
B_FN = (8.0 * np.pi * np.sqrt(2.0 * m)) / (3.0 * h * e)

def calculate_emission_profile(phi_eV=4.5, beta=100.0, T_K=1800.0):
    """
    Обчислення залежності струмів емісії від прикладного електричного поля.
    """
    fields_V_m = np.logspace(5, 8.5, 300) # Поле від 10^5 до 3*10^8 V/m
    
    phi_J = phi_eV * e
    J_rd = A_0 * T_K**2 * np.exp(-phi_J / (k_B * T_K)) * np.ones_like(fields_V_m)
    
    # Ефект Шотткі
    E_local = fields_V_m * beta
    delta_phi_eV = np.sqrt((e**3 * E_local) / (4.0 * np.pi * eps0)) / e
    J_schottky = J_rd * np.exp((delta_phi_eV * e) / (k_B * T_K))
    
    # Автоемісія Фаулера-Нордгейма
    y = delta_phi_eV / phi_eV
    y = np.clip(y, 0.0, 0.99)
    v_y = 1.0 - y**2 + (y**2 / 3.0) * np.log(y + 1e-15)
    
    exponent = - (B_FN * (phi_eV**1.5) * v_y) / E_local
    J_fn = (A_FN * E_local**2 / phi_eV) * np.exp(exponent)
    
    return fields_V_m, J_rd, J_schottky, J_fn

def fit_fowler_nordheim_plot(fields_V_m, J_fn, phi_eV=4.5):
    """
    Лінійна регресія у координатах Фаулера-Нордгейма ln(J/E^2) vs 1/E.
    """
    E_local = fields_V_m * 100.0
    valid_mask = J_fn > 1e-5
    
    x_val = 1.0 / E_local[valid_mask]
    y_val = np.log(J_fn[valid_mask] / (E_local[valid_mask]**2))
    
    slope, intercept = np.polyfit(x_val, y_val, 1)
    extracted_beta = - (B_FN * (phi_eV**1.5)) / slope
    
    return slope, intercept, extracted_beta

if __name__ == "__main__":
    fields, J_rd, J_sch, J_fn = calculate_emission_profile()
    print("Розрахунок успішно виконано.")
