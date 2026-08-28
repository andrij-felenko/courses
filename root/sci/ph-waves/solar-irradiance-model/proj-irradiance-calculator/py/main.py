import math
from dataclasses import dataclass

@dataclass
class SolarPosition:
    zenith_deg: float      # Зенітний кут Сонця (градуси)
    elevation_deg: float   # Висота Сонця над горизонтом (градуси)
    azimuth_deg: float     # Азимут Сонця (градуси від півдня: схід < 0, захід > 0)
    air_mass: float        # Маса повітря (AM)

@dataclass
class IrradianceComponents:
    ghi: float  # Глобальна горизонтальна інсоляція (Вт/м²)
    dni: float  # Пряма нормальна інсоляція (Вт/м²)
    dhi: float  # Дифузна горизонтальна інсоляція (Вт/м²)
    poa: float  # Повна інсоляція на похилій панелі POA (Вт/м²)

def calculate_solar_position(latitude_deg: float, longitude_deg: float,
                             day_of_year: int, hour_utc: float) -> SolarPosition:
    """Обчислення кутів сонячної геометрії за алгоритмом NOAA/Ineichen."""
    lat_rad = math.radians(latitude_deg)
    
    # 1. Кут орбіти (в радіанах)
    b_rad = 2.0 * math.pi * (day_of_year - 81) / 364.0
    
    # 2. Склонення Сонця delta (в радіанах)
    declination_rad = math.radians(23.45) * math.sin(b_rad)
    
    # 3. Рівняння часу EOT (у хвилинах)
    eot_min = 9.87 * math.sin(2.0 * b_rad) - 7.53 * math.cos(b_rad) - 1.5 * math.sin(b_rad)
    
    # 4. Місцевий сонячний час (LST)
    time_offset_min = eot_min + 4.0 * longitude_deg
    lst_hours = hour_utc + time_offset_min / 60.0
    
    # 5. Годинний кут omega (в радіанах)
    hour_angle_rad = math.radians(15.0 * (lst_hours - 12.0))
    
    # 6. Косинус зенітного кута cos(theta_z)
    cos_zenith = (math.sin(lat_rad) * math.sin(declination_rad) +
                  math.cos(lat_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad))
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    
    zenith_rad = math.acos(cos_zenith)
    zenith_deg = math.degrees(zenith_rad)
    elevation_deg = 90.0 - zenith_deg
    
    # 7. Азимут Сонця
    if elevation_deg > -0.5:
        cos_azimuth = ((math.sin(declination_rad) * math.cos(lat_rad) -
                       math.cos(declination_rad) * math.sin(lat_rad) * math.cos(hour_angle_rad)) /
                       math.sin(zenith_rad))
        cos_azimuth = max(-1.0, min(1.0, cos_azimuth))
        azimuth_deg = math.degrees(math.acos(cos_azimuth))
        if math.sin(hour_angle_rad) > 0:
            azimuth_deg = 360.0 - azimuth_deg
    else:
        azimuth_deg = 180.0
        
    # 8. Маса повітря (формула Кастена-Янга)
    if elevation_deg > 0:
        air_mass = 1.0 / (cos_zenith + 0.50572 * math.pow(96.07995 - zenith_deg, -1.6364))
    else:
        air_mass = 0.0
        
    return SolarPosition(zenith_deg, elevation_deg, azimuth_deg, air_mass)

def calculate_irradiance(pos: SolarPosition, day_of_year: int,
                         panel_tilt_deg: float, panel_azimuth_deg: float,
                         albedo: float = 0.2) -> IrradianceComponents:
    """Обчислення складових інсоляції (модель Мейнела + Ізотропна модель Лю-Джордана)."""
    if pos.elevation_deg <= 0:
        return IrradianceComponents(0.0, 0.0, 0.0, 0.0)
        
    # Екстратеріальна інсоляція з урахуванням ексцентриситету
    g_sc = 1361.0
    g_0 = g_sc * (1.0 + 0.033 * math.cos(2.0 * math.pi * day_of_year / 365.0))
    
    # Модель ясного неба (пряме випромінювання DNI)
    dni = g_0 * math.pow(0.7, math.pow(pos.air_mass, 0.678))
    
    # Глобальна горизонтальна (GHI) та дифузна горизонтальна (DHI)
    cos_z = math.cos(math.radians(pos.zenith_deg))
    ghi_direct = dni * cos_z
    dhi = 0.1 * dni  # Емпірична дифузна частка ясного неба
    ghi = ghi_direct + dhi
    
    # Трансформація на похилу площину
    beta_rad = math.radians(panel_tilt_deg)
    gamma_p_rad = math.radians(panel_azimuth_deg)
    gamma_s_rad = math.radians(pos.azimuth_deg)
    zenith_rad = math.radians(pos.zenith_deg)
    
    # Косинус кута падіння променя на панель cos(theta)
    cos_theta = (cos_z * math.cos(beta_rad) +
                 math.sin(zenith_rad) * math.sin(beta_rad) * math.cos(gamma_s_rad - gamma_p_rad))
    cos_theta = max(0.0, cos_theta)
    
    # Компоненти інсоляції POA
    poa_direct = dni * cos_theta
    poa_diffuse = dhi * (1.0 + math.cos(beta_rad)) / 2.0
    poa_ground = ghi * albedo * (1.0 - math.cos(beta_rad)) / 2.0
    
    poa_total = poa_direct + poa_diffuse + poa_ground
    
    return IrradianceComponents(ghi, dni, dhi, poa_total)

# Приклад виклику для Києва (широта 50.45°, довгота 30.52°) 22 червня вполудень (10:00 UTC)
if __name__ == "__main__":
    pos = calculate_solar_position(latitude_deg=50.45, longitude_deg=30.52, day_of_year=173, hour_utc=10.0)
    irr = calculate_irradiance(pos, day_of_year=173, panel_tilt_deg=35.0, panel_azimuth_deg=180.0)
    
    print(f"Зенітний кут: {pos.zenith_deg:.2f}° | Маса повітря AM: {pos.air_mass:.2f}")
    print(f"DNI: {irr.dni:.1f} Вт/м² | GHI: {irr.ghi:.1f} Вт/м² | POA на панелі: {irr.poa:.1f} Вт/м²")
