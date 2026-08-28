import math
from typing import NamedTuple

# Фізичні константи в системі SI
H_PLANCK = 6.62607015e-34    # Стала Планка [Дж·с]
C_LIGHT = 2.99792458e8       # Швидкість світла у вакуумі [м/с]
Q_ELEM = 1.602176634e-19     # Елементарний електричний заряд [Кл]

class SemiconductorSpec(NamedTuple):
    """Специфікація напівпровідникового матеріалу."""
    name: str
    bandgap_ev: float

class BandResult(NamedTuple):
    """Результат аналізу спектрального діапазону."""
    name: str
    power_w_m2: float
    percentage: float

def photon_energy_joules(wavelength_nm: float) -> float:
    """Обчислення енергії фотона в джоулях за довжиною хвилі в нанометрах."""
    wavelength_m = wavelength_nm * 1e-9
    return (H_PLANCK * C_LIGHT) / wavelength_m

def analyze_am15_spectrum(wavelengths: list[float], irradiance_g: list[float]):
    """
    Аналіз спектра AM1.5G: обчислення загальної потужності, 
    фотонного потоку та розподілу по 4 основних діапазонах.
    """
    total_power = 0.0
    uv_power = 0.0
    vis_power = 0.0
    nir_power = 0.0
    ir_power = 0.0
    total_photon_flux = 0.0

    n_points = len(wavelengths)
    for i in range(n_points - 1):
        w1, w2 = wavelengths[i], wavelengths[i + 1]
        e1, e2 = irradiance_g[i], irradiance_g[i + 1]

        dw = w2 - w1
        e_avg = 0.5 * (e1 + e2)
        p_step = e_avg * dw
        total_power += p_step

        w_mid = 0.5 * (w1 + w2)
        e_phot = photon_energy_joules(w_mid)
        photon_flux_step = p_step / e_phot
        total_photon_flux += photon_flux_step

        if w_mid < 400.0:
            uv_power += p_step
        elif w_mid < 700.0:
            vis_power += p_step
        elif w_mid < 1100.0:
            nir_power += p_step
        else:
            ir_power += p_step

    bands = [
        BandResult("УФ (280–400 нм)", uv_power, (uv_power / total_power) * 100.0),
        BandResult("Видимий (400–700 нм)", vis_power, (vis_power / total_power) * 100.0),
        BandResult("Ближній ІЧ (700–1100 нм)", nir_power, (nir_power / total_power) * 100.0),
        BandResult("Далекий ІЧ (>1100 нм)", ir_power, (ir_power / total_power) * 100.0),
    ]

    return total_power, total_photon_flux, bands

def calculate_jsc(wavelengths: list[float], irradiance_g: list[float], bandgap_ev: float) -> float:
    """
    Розрахунок граничного фотоструму короткого замикання J_sc [мА/см²]
    для напівпровідника з шириною забороненої зони bandgap_ev (при EQE = 100%).
    """
    lambda_cut_nm = 1239.841984 / bandgap_ev
    photons_absorbed = 0.0

    for i in range(len(wavelengths) - 1):
        w1, w2 = wavelengths[i], wavelengths[i + 1]
        if w1 >= lambda_cut_nm:
            break

        dw = w2 - w1
        e_avg = 0.5 * (irradiance_g[i] + irradiance_g[i + 1])
        w_mid = 0.5 * (w1 + w2)

        # Обробка часткового кроку сітки на межі поглинання λ_cut
        if w2 > lambda_cut_nm:
            dw = lambda_cut_nm - w1
            w_mid = 0.5 * (w1 + lambda_cut_nm)

        e_phot = photon_energy_joules(w_mid)
        photons_absorbed += (e_avg * dw) / e_phot

    j_sc_a_m2 = Q_ELEM * photons_absorbed
    return j_sc_a_m2 / 10.0  # Конвертація з А/м² у мА/см²

def generate_sample_am15g_data():
    """Синтетична генерація профілю AM1.5G, нормованого на 1000 Вт/м²."""
    wavelengths = []
    irradiance = []
    w = 280.0
    while w <= 4000.0:
        wavelengths.append(w)
        if w < 290.0:
            val = 0.0
        else:
            val = 1.57 * math.exp(-((w - 500.0) / 380.0)**2)
            if 755.0 <= w <= 770.0: val *= 0.35
            if 920.0 <= w <= 970.0: val *= 0.25
            if 1110.0 <= w <= 1160.0: val *= 0.30
            if 1340.0 <= w <= 1450.0: val *= 0.08
            if 1800.0 <= w <= 1950.0: val *= 0.05
        irradiance.append(val)
        step = 1.0 if w < 1000.0 else (5.0 if w < 2000.0 else 20.0)
        w += step

    p_temp, _, _ = analyze_am15_spectrum(wavelengths, irradiance)
    scale = 1000.0 / p_temp
    irradiance = [val * scale for val in irradiance]

    return wavelengths, irradiance

if __name__ == '__main__':
    w_data, irr_data = generate_sample_am15g_data()
    p_tot, ph_tot, band_res = analyze_am15_spectrum(w_data, irr_data)

    print(f"Загальна потужність AM1.5G: {p_tot:.2f} Вт/м²")
    print(f"Загальний фотонний потік: {ph_tot:.3e} фотонів/(м²·с)\n")

    print("Розподіл потужності за діапазонами:")
    for b in band_res:
        print(f"  • {b.name}: {b.power_w_m2:.1f} Вт/м² ({b.percentage:.1f}%)")

    semiconductors = [
        SemiconductorSpec("Кремній (Si)", 1.12),
        SemiconductorSpec("Арсенід галію (GaAs)", 1.42),
        SemiconductorSpec("Телурид кадмію (CdTe)", 1.50),
    ]

    print("\nГраничний фотострум короткого замикання J_sc (при EQE = 100%):")
    for semi in semiconductors:
        jsc = calculate_jsc(w_data, irr_data, semi.bandgap_ev)
        print(f"  • {semi.name} (Eg = {semi.bandgap_ev} еВ): J_sc = {jsc:.2f} мА/см²")
