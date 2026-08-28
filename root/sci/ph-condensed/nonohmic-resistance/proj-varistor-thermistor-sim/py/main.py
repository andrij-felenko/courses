import math

# Фізичні константи
KB = 8.617333262145e-5  # Константа Больцмана, еВ/К
EPS_0 = 8.8541878128e-12  # Електрична стала, Ф/м
E_CHARGE = 1.602176634e-19  # Елементарний заряд, Кл

def simulate_varistor(un_voltage: float, alpha: float, r_grain: float, 
                      u_min: float, u_max: float, steps: int):
    """Моделювання ВАХ ZnO варистора."""
    results = []
    du = (u_max - u_min) / (steps - 1)
    i_ref = 1e-3  # 1 мА
    
    for idx in range(steps):
        u = u_min + idx * du
        i_total = i_ref * ((u / un_voltage) ** alpha)
        
        # Ітераційне врахування опору зерен
        for _ in range(10):
            u_barrier = max(0.0, u - i_total * r_grain)
            i_total = i_ref * ((u_barrier / un_voltage) ** alpha)
            
        r_dyn = u / i_total if i_total > 1e-12 else 1e12
        results.append({"U": u, "I": i_total, "R": r_dyn})
    return results

def simulate_ntc_thermistor(r25: float, b_val: float, delta_mW_K: float, 
                             t_amb_C: float, i_min: float, i_max: float, steps: int):
    """Моделювання саморозігріву NTC термистора та негативного диференціального опору."""
    results = []
    t_amb_K = t_amb_C + 273.15
    delta_W_K = delta_mW_K * 1e-3
    di = (i_max - i_min) / (steps - 1)
    
    for idx in range(steps):
        current = i_min + idx * di
        t_body = t_amb_K
        r_ntc = r25
        
        # Ітераційний тепловий баланс
        for _ in range(30):
            r_ntc = r25 * math.exp(b_val * (1.0 / t_body - 1.0 / 298.15))
            p_heat = (current ** 2) * r_ntc
            t_body = 0.5 * t_body + 0.5 * (t_amb_K + p_heat / delta_W_K)
            
        voltage = current * r_ntc
        results.append({
            "I_mA": current * 1000.0,
            "U": voltage,
            "R": r_ntc,
            "T_C": t_body - 273.15
        })
    return results

def simulate_poole_frenkel(thickness_nm: float, eps_r: float, e_trap_ev: float, 
                           e_min_MV_cm: float, e_max_MV_cm: float, steps: int):
    """Моделювання провідності за ефектом Пуля - Френкеля у діелектрику."""
    results = []
    d_m = thickness_nm * 1e-9
    de = (e_max_MV_cm - e_min_MV_cm) / (steps - 1)
    
    beta_pf_J = math.sqrt((E_CHARGE ** 3) / (math.pi * eps_r * EPS_0))
    beta_pf_eV = beta_pf_J / E_CHARGE
    temp_K = 298.15
    j0 = 1e-6
    
    for idx in range(steps):
        e_field_MV_cm = e_min_MV_cm + idx * de
        e_field_V_m = e_field_MV_cm * 1e8
        
        delta_e_ev = beta_pf_eV * math.sqrt(e_field_V_m)
        eff_trap_ev = e_trap_ev - delta_e_ev
        
        current_density = j0 * (e_field_V_m / 1e6) * math.exp(-eff_trap_ev / (KB * temp_K))
        voltage = e_field_V_m * d_m
        r_eff = voltage / current_density if current_density > 1e-15 else 1e15
        
        results.append({
            "U": voltage,
            "J": current_density,
            "R_eff": r_eff
        })
    return results

if __name__ == "__main__":
    print("=== СИМУЛЯЦІЯ НЕОМІЧНИХ ВАХ (Python 3) ===")
    
    print("\n--- 1. Варистор ZnO (U_N = 430В, alpha = 35) ---")
    var_data = simulate_varistor(430.0, 35.0, 0.5, 300.0, 480.0, 7)
    for row in var_data:
        print(f"U = {row['U']:5.1f} В | I = {row['I']:9.3e} А | R = {row['R']:9.3e} Ом")
        
    print("\n--- 2. NTC Термистор (R25 = 10кОм, Саморозігрів) ---")
    ntc_data = simulate_ntc_thermistor(10000.0, 3950.0, 5.0, 25.0, 0.0002, 0.003, 7)
    for row in ntc_data:
        print(f"I = {row['I_mA']:5.2f} мА | U = {row['U']:5.2f} В | R = {row['R']:7.1f} Ом | T = {row['T_C']:5.1f} °C")
        
    print("\n--- 3. Струм витоку Пуля - Френкеля у Si3N4 (10 нм) ---")
    pf_data = simulate_poole_frenkel(10.0, 3.8, 1.2, 0.5, 3.0, 6)
    for row in pf_data:
        print(f"U = {row['U']:5.2f} В | J = {row['J']:9.3e} А/м^2 | R_eff = {row['R_eff']:9.3e} Ом*м^2")
