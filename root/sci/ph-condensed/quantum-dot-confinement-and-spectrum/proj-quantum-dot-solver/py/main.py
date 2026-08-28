import math
from typing import List, Tuple, Dict

# Фізичні константи в системах СІ та еВ
HBAR = 1.054571817e-34           # Дж·с
EV_TO_JOULE = 1.602176634e-19     # 1 еВ у Джоулях
ELECTRON_MASS = 9.1093837015e-31  # кг
E_CHARGE = 1.602176634e-19        # Кл
EPSILON_0 = 8.8541878128e-12      # Ф/м
SPEED_OF_LIGHT = 299792458        # м/с

class QuantumDotMaterial:
    """Параметри напівпровідникового матеріалу для квантової точки."""
    def __init__(self, name: str, eg_bulk_ev: float, me_eff: float, mh_eff: float, eps_r: float):
        self.name = name
        self.eg_bulk_ev = eg_bulk_ev
        self.me_eff = me_eff * ELECTRON_MASS
        self.mh_eff = mh_eff * ELECTRON_MASS
        self.eps_r = eps_r
        # Зведена ефективна маса
        self.mu_eff = (self.me_eff * self.mh_eff) / (self.me_eff + self.mh_eff)
        # Ефективна рідбергівська енергія
        self.e_rydberg_ev = (self.mu_eff * E_CHARGE**4) / (2.0 * (4.0 * math.pi * EPSILON_0 * self.eps_r)**2 * HBAR**2) / EV_TO_JOULE

def brus_bandgap_ev(material: QuantumDotMaterial, radius_nm: float) -> float:
    """
    Обчислює ширину забороненої зони E_g(R) у еВ за повним рівнянням Бруса.
    """
    if radius_nm <= 0.5:
        raise ValueError("Радіус квантової точки має бути більшим за 0.5 нм для застосовності EMA")

    r_m = radius_nm * 1e-9

    # 1. Кінетичний доданок конфайнменту (1/R²)
    e_conf_joules = (HBAR**2 * math.pi**2) / (2.0 * material.mu_eff * r_m**2)
    e_conf_ev = e_conf_joules / EV_TO_JOULE

    # 2. Кулонівський доданок притягання (1/R)
    e_coulomb_joules = (1.786 * E_CHARGE**2) / (4.0 * math.pi * EPSILON_0 * material.eps_r * r_m)
    e_coulomb_ev = e_coulomb_joules / EV_TO_JOULE

    # 3. Поляризаційна поправка самодії
    e_pol_ev = 0.248 * material.e_rydberg_ev

    # Підсумкова енергія
    return material.eg_bulk_ev + e_conf_ev - e_coulomb_ev - e_pol_ev

def wavelength_from_energy_ev(energy_ev: float) -> float:
    """Перераховує енергію фотона в еВ у довжину хвилі в нм."""
    return (1239.84193 / energy_ev)

def compute_ensemble_spectrum(
    material: QuantumDotMaterial,
    r_mean_nm: float,
    r_std_nm: float,
    energy_grid_ev: List[float],
    homogeneous_gamma_ev: float = 0.03
) -> Tuple[List[float], Dict[str, float]]:
    """
    Обчислює оптичне поглинання ансамблю квантових точок.
    """
    num_samples = 300
    r_min = max(0.6, r_mean_nm - 3.5 * r_std_nm)
    r_max = r_mean_nm + 3.5 * r_std_nm
    dr = (r_max - r_min) / num_samples

    absorption = [0.0] * len(energy_grid_ev)

    for i in range(num_samples):
        r = r_min + (i + 0.5) * dr
        # Імовірність Ґауссова розподілу радіуса
        p_r = (1.0 / (r_std_nm * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * ((r - r_mean_nm) / r_std_nm)**2)
        eg_r = brus_bandgap_ev(material, r)

        for j, e_photon in enumerate(energy_grid_ev):
            # Внесок поглинання з Ґауссовим розширенням лінії
            line_shape = math.exp(-0.5 * ((e_photon - eg_r) / homogeneous_gamma_ev)**2)
            absorption[j] += p_r * line_shape * dr

    # Нормування спектра до 1.0
    max_abs = max(absorption) if max(absorption) > 0 else 1.0
    norm_abs = [a / max_abs for a in absorption]

    # Пошук пікового значення енергії
    max_idx = absorption.index(max(absorption))
    peak_energy = energy_grid_ev[max_idx]
    peak_wl = wavelength_from_energy_ev(peak_energy)

    stats = {
        "peak_energy_ev": peak_energy,
        "peak_wavelength_nm": peak_wl,
        "mean_radius_nm": r_mean_nm,
        "std_radius_nm": r_std_nm
    }

    return norm_abs, stats

# Демонстрація розрахунку для матеріалів CdSe, InP та PbS
if __name__ == "__main__":
    materials = [
        QuantumDotMaterial("CdSe", eg_bulk_ev=1.74, me_eff=0.13, mh_eff=0.45, eps_r=9.3),
        QuantumDotMaterial("InP",  eg_bulk_ev=1.35, me_eff=0.07, mh_eff=0.60, eps_r=12.5),
        QuantumDotMaterial("PbS",  eg_bulk_ev=0.41, me_eff=0.09, mh_eff=0.09, eps_r=17.2)
    ]

    print("=== ОБЧИСЛЕННЯ СПЕКТРАЛЬНИХ ХАРАКТЕРИСТИК КВАНТОВИХ ТОЧОК ===")
    for mat in materials:
        print(f"\n--- Матеріал: {mat.name} (E_g bulk = {mat.eg_bulk_ev} еВ) ---")
        for r_nm in [2.0, 3.5, 5.0]:
            eg_ev = brus_bandgap_ev(mat, r_nm)
            wl_nm = wavelength_from_energy_ev(eg_ev)
            print(f"Радіус R = {r_nm:3.1f} нм | E_g(R) = {eg_ev:5.3f} еВ | Довжина хвилі λ = {wl_nm:6.1f} нм")

        # Розрахунок ансамблю
        e_grid = [1.5 + i * 0.005 for i in range(300)]
        abs_spec, stats = compute_ensemble_spectrum(mat, r_mean_nm=3.0, r_std_nm=0.2, energy_grid_ev=e_grid)
        print(f"Ансамбль R_0 = 3.0±0.2 нм -> Пік поглинання: {stats['peak_energy_ev']:.3f} еВ ({stats['peak_wavelength_nm']:.1f} нм)")
