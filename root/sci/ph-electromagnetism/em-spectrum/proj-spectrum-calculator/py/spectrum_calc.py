# 
# spectrum_calc.py — Програмний аналізатор ЕМ-спектра мовою Python 3.10+
# Включає типізовані датакласи, форматований вивід та перевірку межі іонізації.
# 
import math
from dataclasses import dataclass
from enum import Enum

# Фізичні константи SI
C_SPEED = 299792458.0
H_PLANCK = 6.62607015e-34
EV_JOULE = 1.602176634e-19
WIEN_CONST = 2.89777195e-3
CU_SIGMA = 5.8e7
MU_0 = 4.0 * math.pi * 1e-7

class SpectralBand(Enum):
    RADIO = "Радіохвилі (Radio)"
    MICROWAVE = "Мікрохвилі (Microwave / НВЧ)"
    INFRARED = "Інфрачервоне (IR)"
    VISIBLE = "Видиме світло (Visible)"
    ULTRAVIOLET = "Ультрафіолет (UV)"
    XRAY = "Рентгенівське (X-Ray)"
    GAMMA = "Гамма-випромінювання (Gamma)"

@dataclass(frozen=True)
class SpectrumRecord:
    frequency_hz: float
    wavelength_m: float
    energy_ev: float
    skin_depth_cu_m: float
    wien_temp_k: float
    band: SpectralBand
    is_ionizing: bool

    @classmethod
    def from_frequency(cls, freq_hz: float) -> "SpectrumRecord":
        safe_freq = max(freq_hz, 1e-12)
        wavelength = C_SPEED / safe_freq
        energy_ev = (H_PLANCK * safe_freq) / EV_JOULE
        omega = 2.0 * math.pi * safe_freq
        skin_depth = math.sqrt(2.0 / (omega * MU_0 * CU_SIGMA))
        wien_temp = WIEN_CONST / wavelength

        if safe_freq >= 3.0e19:
            band = SpectralBand.GAMMA
        elif safe_freq >= 3.0e16:
            band = SpectralBand.XRAY
        elif safe_freq >= 7.9e14:
            band = SpectralBand.ULTRAVIOLET
        elif safe_freq >= 4.0e14:
            band = SpectralBand.VISIBLE
        elif safe_freq >= 3.0e11:
            band = SpectralBand.INFRARED
        elif safe_freq >= 3.0e9:
            band = SpectralBand.MICROWAVE
        else:
            band = SpectralBand.RADIO

        return cls(
            frequency_hz=safe_freq,
            wavelength_m=wavelength,
            energy_ev=energy_ev,
            skin_depth_cu_m=skin_depth,
            wien_temp_k=wien_temp,
            band=band,
            is_ionizing=(energy_ev >= 10.0)
        )

    @classmethod
    def from_wavelength(cls, wavelength_m: float) -> "SpectrumRecord":
        safe_lambda = max(wavelength_m, 1e-18)
        return cls.from_frequency(C_SPEED / safe_lambda)

def print_summary(rec: SpectrumRecord) -> None:
    print(f"\n--- Картка ЕМ-сигналу (Python) ---")
    print(f"Частота:         {rec.frequency_hz:.4e} Гц")
    print(f"Довжина хвилі:  {rec.wavelength_m:.4e} м")
    print(f"Енергія кванту: {rec.energy_ev:.4e} еВ")
    print(f"Скін-шар у міді: {rec.skin_depth_cu_m:.4e} м")
    print(f"Температура Віна: {rec.wien_temp_k:.2f} K")
    print(f"Діапазон:        {rec.band.value}")
    print(f"Іонізуюче:       {'ТАК' if rec.is_ionizing else 'НІ'}")
    print(f"----------------------------------")

if __name__ == "__main__":
    # Розрахунок червоного світлодіода 650 нм
    red_led = SpectrumRecord.from_wavelength(650e-9)
    print_summary(red_led)

    # Розрахунок промислового іонізатора 100 ПГц
    uv_c = SpectrumRecord.from_frequency(100e15)
    print_summary(uv_c)
