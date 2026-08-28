import math
from typing import NamedTuple

class SpectralLine(NamedTuple):
    wavelength_nm: float
    intensity: float

class SpectrumPoint(NamedTuple):
    angle_deg: float
    total_intensity: float

class DiffractionGratingSimulator:
    """
    Симулятор спектра дифракційної ґратки.
    Обчислює кутовий розподіл інтенсивності мультипроменевої інтерференції.
    """
    def __init__(self, grooves_per_mm: float, slit_width_um: float, num_grooves: int):
        if grooves_per_mm <= 0:
            raise ValueError("Густина штрихів повинна бути більшою за нуль.")
        if slit_width_um <= 0:
            raise ValueError("Ширина щілини повинна бути більшою за нуль.")
        if num_grooves <= 0:
            raise ValueError("Кількість штрихів повинна бути додатною.")
            
        self.d_meters: float = 1.0e-3 / grooves_per_mm  # період d в метрах
        self.a_meters: float = slit_width_um * 1.0e-6   # ширина a в метрах
        self.num_grooves: int = num_grooves

    def compute_point_intensity(self, theta_rad: float, lines: list[SpectralLine]) -> float:
        """Обчислення сумарної інтенсивності в одній кутовій точці."""
        sin_theta = math.sin(theta_rad)
        total_intensity = 0.0
        
        for line in lines:
            lam = line.wavelength_nm * 1.0e-9  # у метрах
            
            # 1. Однощілинний фазовий параметр beta
            beta = (math.pi * self.a_meters * sin_theta) / lam
            if abs(beta) < 1.0e-9:
                envelope = 1.0
            else:
                envelope = (math.sin(beta) / beta) ** 2
                
            # 2. Багатопроменевий інтерференційний параметр gamma
            gamma = (math.pi * self.d_meters * sin_theta) / lam
            sin_gamma = math.sin(gamma)
            
            if abs(sin_gamma) < 1.0e-9:
                interference = float(self.num_grooves * self.num_grooves)
            else:
                sin_N_gamma = math.sin(self.num_grooves * gamma)
                interference = (sin_N_gamma / sin_gamma) ** 2
                
            total_intensity += line.intensity * envelope * interference
            
        return total_intensity

    def scan_spectrum(self, lines: list[SpectralLine], 
                      start_deg: float = -89.0, 
                      end_deg: float = 89.0, 
                      step_deg: float = 0.01) -> list[SpectrumPoint]:
        """Сканування спектра в заданому кутовому діапазоні."""
        spectrum: list[SpectrumPoint] = []
        curr_deg = start_deg
        
        while curr_deg <= end_deg:
            theta_rad = math.radians(curr_deg)
            intensity = self.compute_point_intensity(theta_rad, lines)
            spectrum.append(SpectrumPoint(curr_deg, intensity))
            curr_deg += step_deg
            
        return spectrum

def analyze_doublet_resolution(spectrum: list[SpectrumPoint], 
                              search_min_deg: float, 
                              search_max_deg: float) -> dict[str, float]:
    """Аналіз контрасту та критерію Релея для подвійного піка."""
    region = [p for p in spectrum if search_min_deg <= p.angle_deg <= search_max_deg]
    if len(region) < 3:
        return {"resolved": False, "contrast": 0.0}

    # Пошук двох найбільших локальних максимумів
    peaks = []
    for i in range(1, len(region) - 1):
        if region[i].total_intensity > region[i-1].total_intensity and \
           region[i].total_intensity > region[i+1].total_intensity:
            peaks.append(region[i])

    peaks.sort(key=lambda p: p.total_intensity, reverse=True)
    if len(peaks) < 2:
        return {"resolved": False, "contrast": 0.0}

    p1, p2 = peaks[0], peaks[1]
    min_angle = min(p1.angle_deg, p2.angle_deg)
    max_angle = max(p1.angle_deg, p2.angle_deg)

    between = [p for p in region if min_angle <= p.angle_deg <= max_angle]
    min_val = min(p.total_intensity for p in between)
    max_val = min(p1.total_intensity, p2.total_intensity)

    contrast = (max_val - min_val) / max_val if max_val > 0 else 0.0
    # За критерієм Релея контраст провалу між піками має бути >= 19%
    resolved = contrast >= 0.19

    return {
        "resolved": resolved,
        "contrast": contrast,
        "peak1_deg": p1.angle_deg,
        "peak2_deg": p2.angle_deg
    }

if __name__ == "__main__":
    # Натрієвий дублет (589.0 нм та 589.6 нм)
    sodium_doublet = [
        SpectralLine(589.0, 1.0),
        SpectralLine(589.6, 0.8)
    ]
    
    # Ґратка 600 lines/mm, a=0.5 мкм, N=1000 штрихів
    sim = DiffractionGratingSimulator(grooves_per_mm=600.0, slit_width_um=0.5, num_grooves=1000)
    spectrum = sim.scan_spectrum(sodium_doublet, start_deg=20.0, end_deg=21.5, step_deg=0.002)
    
    res = analyze_doublet_resolution(spectrum, 20.0, 21.5)
    print(f"Кількість штрихів N = 1000:")
    print(f"  Розділено за Релеєм: {res['resolved']}")
    print(f"  Контраст провалу: {res['contrast']*100:.1f}%")
    print(f"  Пік 1: {res['peak1_deg']:.3f}°, Пік 2: {res['peak2_deg']:.3f}°")
