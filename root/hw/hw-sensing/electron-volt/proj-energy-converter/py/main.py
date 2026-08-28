import math
from typing import Dict, Any

# Фундаментальні константи SI (визначення 2019 року)
C_SPEED: float = 299792458.0              # м/с (точно)
E_CHARGE: float = 1.602176634e-19         # Кл (точно)
KB_JOULE: float = 1.380649e-23            # Дж/К (точно)
HC_EV_NM: float = 1239.84198              # еВ·нм

# Маси спокою частинок у еВ (m c^2)
MASS_ELECTRON_EV: float = 510998.95       # e⁻
MASS_PROTON_EV: float = 938272088.16      # p⁺
MASS_NEUTRON_EV: float = 939565420.52      # n⁰
MASS_ALPHA_EV: float = 3727379400.0       # α (He²⁺)

def calculate_particle_kinematics(energy_ev: float, rest_mass_ev: float, charge_z: int = 1) -> Dict[str, float]:
    """
    Обчислює релятивістську кінетику частинки.
    
    :param energy_ev: Прискорювальна напруга у вольтах або енергія одиночного заряду у еВ.
    :param rest_mass_ev: Маса спокою частинки у еВ (m c^2).
    :param charge_z: Кратність заряду частинки (z = 1 для e⁻/p⁺, z = 2 для α).
    :return: Словник з обчисленими кінетичними параметрами.
    """
    if energy_ev < 0:
        raise ValueError("Кінетична енергія не може бути від'ємною.")
    if rest_mass_ev <= 0:
        raise ValueError("Маса спокою має бути строго додатною.")
    if charge_z <= 0:
        raise ValueError("Кратність заряду має бути додатним цілим числом.")

    # Повна кінетична енергія з урахуванням заряду частинки
    total_kin_ev = energy_ev * charge_z
    eps = total_kin_ev / rest_mass_ev
    gamma = 1.0 + eps

    # Обчислення безрозмірної швидкості β = v/c з вибором точного алгоритму
    if eps < 1e-5:
        # Розклад Тейлора для запобігання втраті точності в мантисі
        beta = math.sqrt(2.0 * eps) * (1.0 - 0.375 * eps + 0.3125 * eps * eps)
    else:
        # Стандартна релятивістська формула
        beta = math.sqrt(1.0 - 1.0 / (gamma * gamma))

    velocity_m_s = beta * C_SPEED

    # Релятивістський імпульс p*c у еВ
    pc_ev = math.sqrt(total_kin_ev * (total_kin_ev + 2.0 * rest_mass_ev))

    # Довжина хвилі де Бройля у нанометрах
    de_broglie_nm = HC_EV_NM / pc_ev if pc_ev > 0 else math.inf

    # Еквівалентна теплова температура T = E / k_B
    energy_joules = total_kin_ev * E_CHARGE
    temp_kelvin = energy_joules / KB_JOULE

    return {
        "total_kin_ev": total_kin_ev,
        "gamma": gamma,
        "beta": beta,
        "velocity_m_s": velocity_m_s,
        "momentum_ev_c": pc_ev,
        "de_broglie_nm": de_broglie_nm,
        "temp_kelvin": temp_kelvin
    }

if __name__ == "__main__":
    print("=== Демонстрація розрахунку кінетики частки ===")
    
    # 1. Низькоенергетичний електрон (100 еВ)
    e100 = calculate_particle_kinematics(100.0, MASS_ELECTRON_EV)
    print(f"Електрон 100 еВ: v = {e100['velocity_m_s']:.3e} м/с, λ_dB = {e100['de_broglie_nm']:.4f} нм")

    # 2. Рентгенівський електрон (50 кеВ)
    e50k = calculate_particle_kinematics(50000.0, MASS_ELECTRON_EV)
    print(f"Електрон 50 кеВ: v/c = {e50k['beta']:.4f}, γ = {e50k['gamma']:.4f}")

    # 3. Альфа-частинка при прискоренні 1 МВ (з зарядом z=2, тобто 2 МеВ)
    alpha = calculate_particle_kinematics(1000000.0, MASS_ALPHA_EV, charge_z=2)
    print(f"Альфа-частинка 1 МВ (2 МеВ): E_k = {alpha['total_kin_ev']/1e6:.1f} МеВ, v = {alpha['velocity_m_s']:.3e} м/с")
