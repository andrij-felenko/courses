import math

# Фізичні фундаментальні константи
EPSILON_0 = 8.8541878176e-12  # Ф/м
Q_E = 1.602176634e-19         # Кл
K_B = 1.380649e-23            # Дж/К
T_KELVIN = 358.15             # 85 °C робоча температура

# База матеріалів: (k_rel, E_g_eV, Phi_B_eV, k_opt)
MATERIALS = {
    "SiO2": (3.9, 8.9, 3.1, 2.13),
    "ONO":  (5.5, 6.0, 2.1, 2.20),
    "ZrO2": (35.0, 5.8, 1.4, 4.84),
    "ZAZ":  (32.0, 5.8, 1.4, 4.50),   # ZrO2 / Al2O3 / ZrO2
    "TiO2": (80.0, 3.2, 0.8, 6.25)
}

def simulate_dram_cell(node_nm, aspect_ratio, mat_name, d_phys_nm, v_dd=0.8):
    """
    Симуляція параметрів конденсатора DRAM для заданого вузла.
    """
    if mat_name not in MATERIALS:
        raise ValueError(f"Невідомий матеріал: {mat_name}")

    k_rel, e_g, phi_b, k_opt = MATERIALS[mat_name]

    # Переведення в одиниці системи СІ
    f_m = node_nm * 1e-9
    d_m = d_phys_nm * 1e-9
    d_pillar = f_m * 0.7
    h_m = d_pillar * aspect_ratio

    # Геометрична площа поверхні циліндричного MIM-стовпчика
    a_cap = math.pi * d_pillar * h_m + math.pi * (d_pillar / 2.0)**2

    # 1. Ємність осередку C_cell (в фемтофарадах fF)
    c_farads = (EPSILON_0 * k_rel * a_cap) / d_m
    c_ff = c_farads * 1e15

    # 2. Еквівалентна товщина оксиду EOT (в нанометрах нм)
    eot_nm = d_phys_nm * (3.9 / k_rel)

    # 3. Напруженість електричного поля E (В/м)
    e_field = v_dd / d_m

    # 4. Струм витоку Пула-Френкеля (А/см²)
    phi_t_j = 1.0 * Q_E  # Глибина пастки 1.0 еВ
    beta_pf = math.sqrt(Q_E / (math.pi * EPSILON_0 * k_opt))
    delta_phi = Q_E * beta_pf * math.sqrt(e_field)
    
    exp_factor = - (phi_t_j - delta_phi) / (K_B * T_KELVIN)
    c_0 = 1.0e-4  # Константа провідності
    j_pf_a_cm2 = (c_0 * e_field * math.exp(exp_factor)) / 100.0

    return {
        "node": node_nm,
        "ar": aspect_ratio,
        "mat": mat_name,
        "d_phys": d_phys_nm,
        "eot": eot_nm,
        "c_cell": c_ff,
        "j_leak": j_pf_a_cm2,
        "pass": c_ff >= 25.0
    }

def main():
    test_cases = [
        (90, 12, "ONO",  5.0, 1.2),
        (45, 25, "ZrO2", 6.0, 1.1),
        (22, 35, "ZAZ",  5.0, 1.0),
        (14, 45, "ZAZ",  4.2, 0.8),
        (10, 50, "TiO2", 3.8, 0.7)
    ]

    print("=" * 86)
    print(f"{'Вузол':<8} | {'AR':<6} | {'Матеріал':<9} | {'d_phys':<8} | {'EOT':<8} | {'C_cell':<10} | {'Виток J_PF':<12} | {'Статус (≥25fF)'}")
    print("=" * 86)

    for node, ar, mat, dp, v in test_cases:
        r = simulate_dram_cell(node, ar, mat, dp, v)
        st = "В НОРМІ" if r["pass"] else "НЕДОСТАТНЬО"
        print(f"{r['node']:>3} нм   | {r['ar']:>4}:1 | {r['mat']:<9} | {r['d_phys']:>6.1f}нм | {r['eot']:>6.2f}нм | {r['c_cell']:>7.2f} fF | {r['j_leak']:>10.2e} | {st}")

    print("=" * 86)

if __name__ == "__main__":
    main()
