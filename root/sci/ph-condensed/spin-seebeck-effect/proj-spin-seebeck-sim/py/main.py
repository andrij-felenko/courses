import math

def simulate_lsse(grad_T, d_pt_nm_list):
    """
    Чисельне моделювання поздовжнього спінового ефекту Зеєбека (LSSE) у гетероструктурі YIG/Pt.
    """
    # Фундаментальні фізичні константи
    hbar = 1.0545718e-34     # Дж·с
    e_charge = 1.6021766e-19 # Кл
    kB = 1.380649e-23        # Дж/К
    
    # Матеріалознавчі параметри YIG та Pt
    Ms = 1.4e5               # А/м
    lambda_mp = 500e-9       # м
    g_mix = 1.2e19           # м^-2
    rho_pt = 20e-8           # Ом·м
    lambda_sd = 1.5e-9       # м
    theta_sh = 0.08          # безрозмірний
    L = 5.0e-3               # м (довжина контакту)

    # 1. Обчислення інжектованого спінового струму J_s^z
    Js_z = (g_mix * kB * lambda_mp / (2.0 * math.pi * Ms)) * grad_T

    print(f"=== Результати розрахунку LSSE (∇T = {grad_T/1e6:.1f} К/мкм) ===")
    print(f"Інжектований спіновий струм J_s^z = {Js_z:.4e} Дж/м²")
    print("-" * 55)
    print(f"{'d_Pt (нм)':<12} | {'F(d_Pt)':<15} | {'V_ISHE (мкВ)':<15}")
    print("-" * 55)

    results = []
    for d_nm in d_pt_nm_list:
        d_pt = d_nm * 1e-9
        x = d_pt / (2.0 * lambda_sd)
        
        # Обробка чисельної стійкості при малому аргументі
        if x < 1e-4:
            F_factor = 1.0 / (2.0 * lambda_sd)
        else:
            F_factor = math.tanh(x) / d_pt
        
        # Обчислення вихідної напруги V_ISHE
        v_ishe = (L * theta_sh * rho_pt * lambda_sd * (2.0 * e_charge / hbar) * Js_z * F_factor)
        v_microvolts = v_ishe * 1e6
        results.append((d_nm, v_microvolts))
        print(f"{d_nm:<12.1f} | {F_factor:<15.4e} | {v_microvolts:<15.4f}")
    
    return results

if __name__ == "__main__":
    grad_T = 1.0e6  # 1 К/мкм
    thicknesses = [0.5, 1.0, 1.5, 3.0, 4.5, 6.0, 10.0]
    simulate_lsse(grad_T, thicknesses)
