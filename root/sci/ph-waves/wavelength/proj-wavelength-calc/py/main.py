import math
from dataclasses import dataclass
from typing import List

# Фізична константа швидкості світла у вакуумі (м/с)
SPEED_OF_LIGHT_VACUUM: float = 299792458.0

@dataclass
class WaveProperties:
    """Структура даних для збереження розрахованих параметрів хвилі."""
    frequency_hz: float
    speed_m_s: float
    wavelength_m: float
    wavenumber_k: float  # просторова частота, рад/м
    period_s: float

def acoustic_speed_in_air(temperature_celsius: float) -> float:
    """Обчислення швидкості звуку в сухому повітрі при заданій температурі (°C)."""
    return 331.3 * math.sqrt(1.0 + temperature_celsius / 273.15)

def em_wavelength_in_medium(frequency_hz: float, refractive_index: float) -> WaveProperties:
    """Обчислення параметрів електромагнітної хвилі в середовищі з показником заломлення n."""
    if frequency_hz <= 0.0 or refractive_index <= 0.0:
        raise ValueError("Частота та показник заломлення мусять бути додатними числами")
    
    speed = SPEED_OF_LIGHT_VACUUM / refractive_index
    wavelength = speed / frequency_hz
    wavenumber = 2.0 * math.pi / wavelength
    period = 1.0 / frequency_hz
    
    return WaveProperties(
        frequency_hz=frequency_hz,
        speed_m_s=speed,
        wavelength_m=wavelength,
        wavenumber_k=wavenumber,
        period_s=period
    )

def calculate_standing_wave_nodes(length_m: float, wavelength_m: float) -> List[float]:
    """Обчислення координат вузлів стоячої хвилі на відрізку довжиною L."""
    if wavelength_m <= 0.0 or length_m < 0.0:
        return []
    
    node_spacing = wavelength_m / 2.0
    nodes = []
    current_pos = 0.0
    # Мала поправка 1e-9 запобігає втраті останнього вузла через округлення float
    while current_pos <= length_m + 1e-9:
        nodes.append(current_pos)
        current_pos += node_spacing
    return nodes

def main() -> None:
    # 1. Акустична хвиля 40 кГц (ультразвуковий дальномір) у повітрі при 20°C
    f_us = 40000.0
    v_air = acoustic_speed_in_air(20.0)
    lambda_air = v_air / f_us
    k_air = 2.0 * math.pi / lambda_air
    
    print(f"=== 1. Акустика (40 кГц у повітрі при 20°C) ===")
    print(f"Швидкість звуку: {v_air:.2f} м/с")
    print(f"Довжина хвилі:   {lambda_air * 1000.0:.3f} мм")
    print(f"Хвильове число:  {k_air:.2f} рад/м")

    # 2. Оптична хвиля 1550 нм у кварцовому волокні (n = 1.444)
    f_opt = 193.4e12  # 193.4 ТГц (C-band)
    em_prop = em_wavelength_in_medium(f_opt, refractive_index=1.444)
    
    print(f"\n=== 2. Волоконна оптика (193.4 ТГц, C-band) ===")
    print(f"Швидкість у волокні: {em_prop.speed_m_s / 1e8:.4f} × 10⁸ м/с")
    print(f"Довжина хвилі:       {em_prop.wavelength_m * 1e9:.2f} нм")
    print(f"Хвильове число k:    {em_prop.wavenumber_k / 1e6:.4f} × 10⁶ рад/м")

    # 3. Вузли стоячої хвилі у трубі довжиною 1.0 м на частоті 500 Гц
    v_sound = acoustic_speed_in_air(20.0)
    lambda_500 = v_sound / 500.0
    nodes = calculate_standing_wave_nodes(1.0, lambda_500)
    print(f"\n=== 3. Вузли стоячої хвилі (500 Гц, L = 1.0 м) ===")
    print(f"Довжина хвилі λ: {lambda_500:.3f} м (крок між вузлами λ/2 = {lambda_500/2:.3f} м)")
    print(f"Координати вузлів (м): {[round(n, 3) for n in nodes]}")

if __name__ == "__main__":
    main()
