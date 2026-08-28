import math
from dataclasses import dataclass, field
from typing import List, Tuple

PLANCK_H: float = 6.62607015e-34
SPEED_OF_LIGHT_C: float = 299792458.0
ELEMENTARY_CHARGE_E: float = 1.602176634e-19
BOLTZMANN_KB: float = 1.380649e-23

@dataclass(frozen=True)
class OpticalComponent:
    name: str
    transmittance: float

@dataclass
class PhotonBudgetConfig:
    wavelength_m: float = 1550e-9
    power_tx_w: float = 0.050
    distance_m: float = 2000.0
    atten_db_per_km: float = 2.5
    divergence_rad: float = 0.0015
    beam_waist_m: float = 0.005
    rx_aperture_m: float = 0.100
    
    quantum_efficiency: float = 0.85
    dark_current_a: float = 2e-9
    load_resistor_ohm: float = 50.0
    temperature_k: float = 300.0
    bandwidth_hz: float = 125e6
    
    optical_cascade: List[OpticalComponent] = field(default_factory=list)

@dataclass
class PhotonBudgetResult:
    photon_energy_j: float
    rx_power_w: float
    rx_power_dbm: float
    photoelectrons_per_bit: float
    sigma_shot_e: float
    sigma_dark_e: float
    sigma_thermal_e: float
    sigma_total_e: float
    snr_linear: float
    snr_db: float
    link_margin_db: float

def calculate_photon_budget(config: PhotonBudgetConfig, required_snr_db: float = 15.6) -> PhotonBudgetResult:
    # 1. Енергія кванта
    photon_energy = (PLANCK_H * SPEED_OF_LIGHT_C) / config.wavelength_m
    
    # 2. Каскад оптичних елементів
    cascade_eff = 1.0
    for comp in config.optical_cascade:
        cascade_eff *= comp.transmittance
        
    # 3. Атмосферне / волоконне згасання
    dist_km = config.distance_m / 1000.0
    channel_loss_db = config.atten_db_per_km * dist_km
    channel_eff = 10.0 ** (-channel_loss_db / 10.0)
    
    # 4. Геометричні втрати
    spot_radius = config.beam_waist_m + config.distance_m * math.tan(config.divergence_rad)
    spot_area = math.pi * (spot_radius ** 2)
    rx_radius = config.rx_aperture_m / 2.0
    rx_area = math.pi * (rx_radius ** 2)
    geom_eff = min(1.0, rx_area / spot_area)
    
    # 5. Приймана потужність
    rx_power_w = config.power_tx_w * cascade_eff * channel_eff * geom_eff
    rx_power_dbm = 10.0 * math.log10(rx_power_w / 1e-3)
    rx_photon_rate = rx_power_w / photon_energy
    
    # 6. Сигнал у фотоелектронах на біт
    dt = 1.0 / (2.0 * config.bandwidth_hz)
    photoelectrons = config.quantum_efficiency * rx_photon_rate * dt
    
    # 7. Шуми
    sigma_shot = math.sqrt(photoelectrons)
    dark_electrons = (config.dark_current_a * dt) / ELEMENTARY_CHARGE_E
    sigma_dark = math.sqrt(dark_electrons)
    
    thermal_current_sq = (4.0 * BOLTZMANN_KB * config.temperature_k * config.bandwidth_hz) / config.load_resistor_ohm
    thermal_current_rms = math.sqrt(thermal_current_sq)
    sigma_thermal = (thermal_current_rms * dt) / ELEMENTARY_CHARGE_E
    
    sigma_total = math.hypot(sigma_shot, sigma_dark, sigma_thermal)
    
    # 8. SNR та Margin
    snr_lin = photoelectrons / sigma_total
    snr_db = 20.0 * math.log10(snr_lin)
    margin_db = snr_db - required_snr_db
    
    return PhotonBudgetResult(
        photon_energy_j=photon_energy,
        rx_power_w=rx_power_w,
        rx_power_dbm=rx_power_dbm,
        photoelectrons_per_bit=photoelectrons,
        sigma_shot_e=sigma_shot,
        sigma_dark_e=sigma_dark,
        sigma_thermal_e=sigma_thermal,
        sigma_total_e=sigma_total,
        snr_linear=snr_lin,
        snr_db=snr_db,
        link_margin_db=margin_db
    )

if __name__ == "__main__":
    cfg = PhotonBudgetConfig(
        optical_cascade=[
            OpticalComponent("Коліматор AR", 0.98),
            OpticalComponent("Спектральний фільтр", 0.85),
            OpticalComponent("Дихроїчна призма", 0.95)
        ]
    )
    res = calculate_photon_budget(cfg, required_snr_db=15.6)
    
    print("=== ФОТОННИЙ БЮДЖЕТ ОПТИЧНОЇ СИСТЕМИ (Python) ===")
    print(f"Енергія фотона:             {res.photon_energy_j:.3e} Дж")
    print(f"Приймана потужність:        {res.rx_power_w * 1e6:.3f} мкВт ({res.rx_power_dbm:.2f} дБм)")
    print(f"Сигнал на біт:              {res.photoelectrons_per_bit:.0f} e-")
    print(f"Дробовий шум:               {res.sigma_shot_e:.1f} e-")
    print(f"Тепловий шум:               {res.sigma_thermal_e:.1f} e-")
    print(f"Сумарний шум:               {res.sigma_total_e:.1f} e-")
    print(f"Відношення Сигнал/Шум (SNR): {res.snr_db:.2f} дБ (лінійне: {res.snr_linear:.1f})")
    print(f"Запас лінії (Link Margin):  {res.link_margin_db:+.2f} дБ")
