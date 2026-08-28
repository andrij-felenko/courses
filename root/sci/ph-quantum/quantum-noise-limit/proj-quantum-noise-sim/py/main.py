import math
import numpy as np

# Фізичні константи в системі СІ
HBAR = 1.054571817e-34  # Зведена стала Планка [Дж·с]
KB = 1.380649e-23        # Стала Больцмана [Дж/К]
QE = 1.602176634e-19     # Елементарний заряд [Кл]

def callen_welton_noise(r_ohm: float, temp_k: float, freq_hz: float) -> float:
    """
    Обчислює спектральну густину шуму напруги S_V(nu) за теоремою Каллена — Велтона:
    S_V(nu) = 2 * R * h * nu * coth(h * nu / (2 * k_B * T))
    """
    if r_ohm < 0 or temp_k < 0 or freq_hz < 0:
        raise ValueError("Фізичні параметри повинні бути невід'ємними.")
        
    h_nu = 2.0 * math.pi * HBAR * freq_hz
    if temp_k <= 1e-9:
        # При абсолютному нулі залишаються лише нульові вакуумні флуктуації
        return 2.0 * r_ohm * h_nu
    
    x = h_nu / (2.0 * KB * temp_k)
    # Числово-стійкий розклад coth(x) для малих та великих x
    if x < 1e-4:
        coth_val = 1.0 / x + x / 3.0
    elif x > 50.0:
        coth_val = 1.0
    else:
        coth_val = (math.exp(x) + math.exp(-x)) / (math.exp(x) - math.exp(-x))
    
    return 2.0 * r_ohm * h_nu * coth_val

def shot_noise_tunnel_junction(voltage_v: float, temp_k: float, r_junction: float, fano_factor: float = 1.0) -> float:
    """
    Обчислює спектральну густину струмового шуму S_I(V) тунельного контакту:
    S_I(V) = F * e * I * coth(e * V / (2 * k_B * T))
    """
    if r_junction <= 0:
        raise ValueError("Опір контакту повинен бути додатним.")
        
    current_i = voltage_v / r_junction
    e_v = QE * abs(voltage_v)
    
    if temp_k <= 1e-9:
        # Границя T -> 0 K: чистий дробовий шум Шотткі
        return 2.0 * fano_factor * QE * abs(current_i)
        
    x = e_v / (2.0 * KB * temp_k)
    if x < 1e-4:
        coth_val = 1.0 / x + x / 3.0
    elif x > 50.0:
        coth_val = 1.0
    else:
        coth_val = (math.exp(x) + math.exp(-x)) / (math.exp(x) - math.exp(-x))
        
    return fano_factor * QE * abs(current_i) * coth_val

def sql_displacement_noise(power_mw: float, mass_kg: float, omega_0: float, freq_hz: float) -> tuple[float, float, float]:
    """
    Обчислює складові шуму зміщення optomechanical sensor:
    повертає (S_imp, S_back, S_total).
    """
    if power_mw <= 0 or mass_kg <= 0:
        raise ValueError("Потужність та маса повинні бути додатними.")
        
    p_watts = power_mw * 1e-3
    omega = 2.0 * math.pi * freq_hz
    susceptibility = 1.0 / (mass_kg * abs(omega**2 - omega_0**2))
    
    # Коефіцієнт зв'язку зондуючого променя (умовні одиниці для демонстрації оптимізації)
    coupling = 1e-12
    s_imp = coupling / p_watts
    s_back = coupling * p_watts * (susceptibility**2) * 1e24
    s_tot = s_imp + s_back
    
    return s_imp, s_back, s_tot

def run_simulation():
    r_resistor = 50.0  # 50 Ом стандартний НВЧ імпеданс
    t_cryo = 0.020     # 20 мК (мікрокельвіновий кріостат розчинення)
    
    print("=== 1. Квантовий шум Джонсона — Найквіста S_V(nu) ===")
    freqs = [1e6, 1e9, 5e9, 20e9, 100e9]
    for f in freqs:
        sv = callen_welton_noise(r_resistor, t_cryo, f)
        sv_classical = 4.0 * r_resistor * KB * t_cryo
        ratio = sv / sv_classical
        print(f"f = {f/1e9:6.2f} ГГц | S_V = {sv:.3e} В²/Гц | Перевищення над класичним: {ratio:6.2f}x")
        
    print("\n=== 2. Дробовий шум Шотткі S_I(V) у тунельному контакті ===")
    voltages = [0.001, 0.010, 0.100]
    for v in voltages:
        si_p = shot_noise_tunnel_junction(v, t_cryo, 1000.0, fano_factor=1.0)
        si_sub = shot_noise_tunnel_junction(v, t_cryo, 1000.0, fano_factor=0.5)
        print(f"V = {v*1e3:5.1f} мВ | S_I (F=1.0) = {si_p:.3e} А²/Гц | S_I (F=0.5) = {si_sub:.3e} А²/Гц")

    print("\n=== 3. Пошук Стандартної квантової межі (SQL) ===")
    m_mirror = 1e-9  # 1 мг механічний резонатор
    w0 = 2.0 * math.pi * 1e5  # 100 кГц
    powers = np.linspace(0.1, 10.0, 5)
    for p in powers:
        s_imp, s_back, s_tot = sql_displacement_noise(p, m_mirror, w0, 1e5 + 10)
        print(f"P = {p:4.1f} мВт | S_imp = {s_imp:.3e} | S_back = {s_back:.3e} | S_tot = {s_tot:.3e}")

if __name__ == "__main__":
    run_simulation()
