import math
from typing import Dict, List, Tuple

# Фізичні константи в природній системі одиниць
HBAR_C = 0.19732698  # ҐеВ * фм (ħc)
M_Z = 91.1876       # Маса Z-бозона в ҐеВ
ALPHA_S_MZ = 0.1179  # α_s(M_Z)

def calculate_yukawa_cross_section(
    energy_gev: float,
    angle_rad: float,
    coupling: float,
    boson_mass_gev: float,
    target_mass_gev: float
) -> float:
    """Обчислює диференціальний переріз розсіяння dσ/dΩ (в барнах/дср) у борнівському наближенні."""
    k = math.sqrt(max(0.0, energy_gev**2 - target_mass_gev**2)) if energy_gev > target_mass_gev else energy_gev
    q_transfer = 2.0 * k * math.sin(angle_rad / 2.0)  # Переданий імпульс у ҐеВ
    
    mu = boson_mass_gev  # Масовий параметр в ҐеВ
    denominator = q_transfer**2 + mu**2
    
    amplitude_fm = (2.0 * target_mass_gev * coupling * HBAR_C) / (denominator if denominator > 0 else 1e-12)
    cross_section_fm2 = amplitude_fm**2
    return cross_section_fm2 * 0.01  # Перетворення у барни (1 фм² = 0.01 б)

def calculate_total_yukawa_cross_section(
    energy_gev: float,
    coupling: float,
    boson_mass_gev: float,
    target_mass_gev: float,
    num_steps: int = 1000
) -> float:
    """Чисельне інтегрування dσ/dΩ по куту θ для отримання повного перерізу σ_tot."""
    dtheta = math.pi / num_steps
    total_sigma = 0.0
    
    for i in range(num_steps):
        theta = (i + 0.5) * dtheta
        dsig = calculate_yukawa_cross_section(energy_gev, theta, coupling, boson_mass_gev, target_mass_gev)
        total_sigma += dsig * 2.0 * math.pi * math.sin(theta) * dtheta
        
    return total_sigma

def running_coupling_qcd(q_gev: float, n_flavors: int = 5) -> float:
    """Обчислює α_s(Q²) для квантової хромодинаміки з урахуванням асимптотичної свободи."""
    if q_gev <= 0.3:
        return 1.0  # Границя конфайнменту при низьких енергіях
    
    beta_0 = 11.0 - (2.0 / 3.0) * n_flavors
    ln_ratio = math.log((q_gev / M_Z)**2)
    denom = 1.0 + (beta_0 * ALPHA_S_MZ / (4.0 * math.pi)) * ln_ratio
    return ALPHA_S_MZ / max(0.01, denom)

if __name__ == "__main__":
    print("=== Обчислення перерізу розсіяння та констант взаємодії ===")
    angles_deg = [10, 30, 60, 90, 120, 150]
    
    print("\nДиференціальний переріз Юкави (p-p розсіяння через піон, E=0.5 ҐеВ):")
    for deg in angles_deg:
        rad = math.radians(deg)
        dsig = calculate_yukawa_cross_section(0.5, rad, coupling=1.0, boson_mass_gev=0.1395, target_mass_gev=0.938)
        print(f"  Кут {deg:3d}°: dσ/dΩ = {dsig:.6e} барн/дср")
        
    sigma_tot = calculate_total_yukawa_cross_section(0.5, coupling=1.0, boson_mass_gev=0.1395, target_mass_gev=0.938)
    print(f"\nПовний переріз розсіяння σ_tot = {sigma_tot:.6f} барн")
    
    print("\nЕволюція константи сильноі взаємодії α_s(Q):")
    for q in [1.0, 5.0, 10.0, 91.2, 500.0, 10000.0]:
        alpha_s = running_coupling_qcd(q)
        print(f"  Q = {q:7.1f} ҐеВ: α_s(Q) = {alpha_s:.4f}")
