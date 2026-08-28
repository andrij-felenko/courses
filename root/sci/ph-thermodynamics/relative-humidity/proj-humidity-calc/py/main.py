import math
from typing import Tuple, Optional

MAGNUS_A = 6.112    # гПа
MAGNUS_B = 17.67
MAGNUS_C = 243.5    # °C
PSYCHRO_A = 0.000662 # К⁻¹

def saturation_vapor_pressure(temp_celsius: float) -> float:
    """Обчислення тиску насиченої водяної пари (гПа)."""
    return MAGNUS_A * math.exp((MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius))

def dew_point(temp_celsius: float, relative_humidity_pct: float) -> Optional[float]:
    """Обчислення температури точки роси (°C)."""
    if not (0.0 < relative_humidity_pct <= 100.0):
        return None
    gamma = math.log(relative_humidity_pct / 100.0) + (MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius)
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma)

def psychrometric_relative_humidity(t_dry: float, t_wet: float, pressure_hpa: float = 1013.25) -> Tuple[float, float]:
    """Обчислення відносної вологості (%) та точки роси (°C) за психрометром."""
    if t_wet > t_dry:
        raise ValueError("Температура вологого термометра не може бути вищою за сухий")
    
    e_s_wet = saturation_vapor_pressure(t_wet)
    e_s_dry = saturation_vapor_pressure(t_dry)
    actual_e = e_s_wet - PSYCHRO_A * pressure_hpa * (t_dry - t_wet)
    
    rh = max(0.0, min(100.0, (actual_e / e_s_dry) * 100.0))
    td = dew_point(t_dry, rh)
    return rh, td

if __name__ == "__main__":
    t_dry, t_wet, p = 25.0, 18.5, 1013.25
    rh, td = psychrometric_relative_humidity(t_dry, t_wet, p)
    print(f"Психрометрія (Python): T_dry={t_dry}°C, T_wet={t_wet}°C -> RH={rh:.2f}%, T_d={td:.2f}°C")
