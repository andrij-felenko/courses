# ⚙️ Обчислення сонячної позиції та компонентів інсоляції

Цей практичний модуль демонструє повний алгоритм розрахунку положення Сонця на небосхилі, маси повітря та розбиття інсоляції на пряму, дифузну та відбиту компоненти для довільно похиленого фотомодуля.

### Фізико-математична основа обчислювального модуля

Автоматизоване моделювання сонячного випромінювання необхідне для проектування фотоелектричних систем, оптимізації кутів установки сонячних панелей, а також для побудови систем автоматичного трекінгу (стеження за Сонцем на двовісних та одновосних опорних конструкціях). Для обчислення падаючого потоку в будь-якій точці земної кулі в довільний момент часу обчислювальна система виконує послідовно п'ять розрахункових кроків:

1. **Розрахунок астрономічних параметрів орбіти**:
   Земля рухається навколо Сонця по еліптичній орбіті з ексцентриситетом `e ≈ 0.0167`. Це спричиняє щорічну варіацію відстані між Землею та Сонцем у межах ±3.3%. Позаатмосферна сонячна інсоляція `G_0` обчислюється з урахуванням порядкового дня року `n` (від 1 до 365):

   ```
   G_0 = G_sc · (1 + 0.033 · cos(2π · n / 365))
   ```

   Склонення Сонця `δ` (кут між екваторіальною площиною Землі та напрямком на Сонце) варіюється протягом року від `-23.45°` під час зимового сонцестояння до `+23.45°` під час літнього сонцестояння і описується формулою:

   ```
   δ = 23.45° · sin(2π · (284 + n) / 365)
   ```

2. **Обчислення рівняння часу (EOT) та місцевого сонячного часу**:
   Через нерівномірність руху Землі по еліптичній орбіті та нахил земної осі істинний сонячний час відхиляється від середнього цивільного часу. Ця різниця описується рівнянням часу `EOT` (*Equation of Time*, у хвилинах):

   ```
   B = 2π · (n - 81) / 364
   EOT = 9.87 · sin(2B) - 7.53 · cos(B) - 1.5 · sin(B)
   ```

   На основі `EOT` та довготи спостерігача `λ` (у градусах) обчислюється місцевий сонячний час `LST` (*Local Solar Time*) та годинний кут Сонця `ω`:

   ```
   LST = hour_utc + (EOT + 4.0 · λ) / 60.0
   ω = 15° · (LST - 12.0)
   ```

3. **Обчислення кутів сонячної позиції**:
   Зенітний кут Сонця `θ_z` визначається на основі сферичної тригонометрії:

   ```
   cos(θ_z) = sin(φ) · sin(δ) + cos(φ) · cos(δ) · cos(ω)
   ```

   де `φ` — географічна широта точки спостереження. Сонячна висота дорівнює `α_s = 90° - θ_z`.

4. **Оцінювання маси повітря та компонентів ясного неба**:
   Маса повітря `AM` обчислюється за формулою Кастена — Янга. Пряма нормальна інсоляція `DNI` розраховується за прозорісною моделлю Мейнела:

   ```
   DNI = G_0 · 0.7^(AM^0.678)
   ```

   Глобальна горизонтальна інсоляція складається з прямої та дифузної компоненти:

   ```
   GHI = DNI · cos(θ_z) + DHI
   ```

5. **Перерахунок інсоляції на похилу площину POA (*Plane of Array*)**:
   Для фотомодуля з кутом нахилу `β` та азимутом `γ` загальна поглинена інсоляція `G_T` є сумою трьох складових (ізотропна модель Лю-Джордана):

   ```
   G_T = G_{b,T} + G_{d,T} + G_{r,T}
   G_{b,T} = DNI · cos(θ)
   G_{d,T} = DHI · (1 + cos(β)) / 2
   G_{r,T} = GHI · ρ_g · (1 - cos(β)) / 2
   ```

   де `ρ_g` — альбедо навколишньої поверхні (для трави `ρ_g ≈ 0.2`, для свіжого снігу `ρ_g ≈ 0.8`).

### Покроковий числовий приклад розрахунку

Розглянемо практичний приклад розрахунку сонячної інсоляції для міста Києва (широта `φ = 50.45° N`, довгота `λ = 30.52° E`) на день літнього сонцестояння (22 червня, `n = 173`) о 10:00 за часом UTC (13:00 за київським літнім часом EEST). Фотоелектрична панель встановлена з нахилом `β = 35°` під південним азимутом (`γ = 0°`).

- **Крок 1**: Склонення Сонця `δ = 23.45° · sin(360° · (284 + 173) / 365) ≈ +23.44°`.
- **Крок 2**: Рівняння часу `B = 2π · (173 - 81) / 364 ≈ 1.589 рад`. `EOT = 9.87·sin(3.178) - 7.53·cos(1.589) - 1.5·sin(1.589) ≈ -1.5 хвилини`.
- **Крок 3**: Сонячний час `LST = 10.0 + (-1.5 + 4.0 · 30.52) / 60.0 = 12.01 години`. Годинний кут `ω = 15° · (12.01 - 12.0) = +0.15°` (майже точний сонячний полудень).
- **Крок 4**: Косинус зенітного кута `cos(θ_z) = sin(50.45°)·sin(23.44°) + cos(50.45°)·cos(23.44°)·cos(0.15°) ≈ 0.7711 · 0.3978 + 0.6368 · 0.9175 · 1.0 = 0.3067 + 0.5843 = 0.8910`.
- **Крок 5**: Зенітний кут `θ_z = arccos(0.8910) ≈ 27.00°`. Висота Сонця над горизонтом `α_s = 90° - 27° = 63.00°`.
- **Крок 6**: Маса повітря `AM = 1 / cos(27.00°) ≈ 1.122`.
- **Крок 7**: Позаатмосферний потік `G_0 = 1361 · (1 + 0.033 · cos(2π · 173 / 365)) ≈ 1316.5 Вт/м²`.
- **Крок 8**: Пряма нормальна інсоляція `DNI = 1316.5 · 0.7^(1.122^0.678) ≈ 889 Вт/м²`.
- **Крок 9**: Кут падіння на панель `cos(θ) = cos(27°)·cos(35°) + sin(27°)·sin(35°)·cos(0°) ≈ 0.8910 · 0.8192 + 0.4540 · 0.5736 · 1.0 = 0.7299 + 0.2604 = 0.9903` (`θ ≈ 8.0°`).
- **Крок 10**: Пряма складова на панелі `G_{b,T} = 889 · 0.9903 ≈ 880 Вт/м²`. Дифузна складова `G_{d,T} ≈ 89 · (1 + 0.8192) / 2 ≈ 81 Вт/м²`. Загальна інсоляція на похилій панелі `POA G_T ≈ 966 Вт/м²`.

### Реалізація калькулятора інсоляції

Нижче наведено паралельну реалізацію алгоритму двома мовами програмування — Python та C++. Обидва варіанти є повністю тотожними за логікою та ідіоматичними для своїх екосистем.

:::tabs
```py
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
```
```cpp
#include <iostream>
#include <cmath>
#include <algorithm>
#include <numbers>
#include <iomanip>

struct SolarPosition {
    double zenith_deg;     // Зенітний кут Сонця (градуси)
    double elevation_deg;  // Висота Сонця над горизонтом (градуси)
    double azimuth_deg;    // Азимут Сонця (градуси)
    double air_mass;       // Маса повітря (AM)
};

struct IrradianceComponents {
    double ghi;  // Глобальна горизонтальна інсоляція (Вт/м²)
    double dni;  // Пряма нормальна інсоляція (Вт/м²)
    double dhi;  // Дифузна горизонтальна інсоляція (Вт/м²)
    double poa;  // Повна інсоляція на похилій панелі POA (Вт/м²)
};

constexpr double deg_to_rad(double deg) {
    return deg * std::numbers::pi / 180.0;
}

constexpr double rad_to_deg(double rad) {
    return rad * 180.0 / std::numbers::pi;
}

SolarPosition calculate_solar_position(double latitude_deg, double longitude_deg,
                                       int day_of_year, double hour_utc) {
    const double lat_rad = deg_to_rad(latitude_deg);
    
    // 1. Кут орбіти
    const double b_rad = 2.0 * std::numbers::pi * (day_of_year - 81) / 364.0;
    
    // 2. Склонення Сонця delta
    const double declination_rad = deg_to_rad(23.45) * std::sin(b_rad);
    
    // 3. Рівняння часу EOT (у хвилинах)
    const double eot_min = 9.87 * std::sin(2.0 * b_rad) - 7.53 * std::cos(b_rad) - 1.5 * std::sin(b_rad);
    
    // 4. Місцевий сонячний час LST
    const double time_offset_min = eot_min + 4.0 * longitude_deg;
    const double lst_hours = hour_utc + time_offset_min / 60.0;
    
    // 5. Годинний кут omega
    const double hour_angle_rad = deg_to_rad(15.0 * (lst_hours - 12.0));
    
    // 6. Косинус зенітного кута
    double cos_zenith = std::sin(lat_rad) * std::sin(declination_rad) +
                        std::cos(lat_rad) * std::cos(declination_rad) * std::cos(hour_angle_rad);
    cos_zenith = std::clamp(cos_zenith, -1.0, 1.0);
    
    const double zenith_rad = std::acos(cos_zenith);
    const double zenith_deg = rad_to_deg(zenith_rad);
    const double elevation_deg = 90.0 - zenith_deg;
    
    // 7. Азимут Сонця
    double azimuth_deg = 180.0;
    if (elevation_deg > -0.5) {
        double cos_azimuth = (std::sin(declination_rad) * std::cos(lat_rad) -
                              std::cos(declination_rad) * std::sin(lat_rad) * std::cos(hour_angle_rad)) /
                             std::sin(zenith_rad);
        cos_azimuth = std::clamp(cos_azimuth, -1.0, 1.0);
        azimuth_deg = rad_to_deg(std::acos(cos_azimuth));
        if (std::sin(hour_angle_rad) > 0) {
            azimuth_deg = 360.0 - azimuth_deg;
        }
    }
    
    // 8. Маса повітря (Кастен-Янг)
    double air_mass = 0.0;
    if (elevation_deg > 0.0) {
        air_mass = 1.0 / (cos_zenith + 0.50572 * std::pow(96.07995 - zenith_deg, -1.6364));
    }
    
    return SolarPosition{zenith_deg, elevation_deg, azimuth_deg, air_mass};
}

IrradianceComponents calculate_irradiance(const SolarPosition& pos, int day_of_year,
                                         double panel_tilt_deg, double panel_azimuth_deg,
                                         double albedo = 0.2) {
    if (pos.elevation_deg <= 0.0) {
        return IrradianceComponents{0.0, 0.0, 0.0, 0.0};
    }
    
    constexpr double g_sc = 1361.0;
    const double g_0 = g_sc * (1.0 + 0.033 * std::cos(2.0 * std::numbers::pi * day_of_year / 365.0));
    
    // Пряме випромінювання DNI (модель Мейнела)
    const double dni = g_0 * std::pow(0.7, std::pow(pos.air_mass, 0.678));
    
    const double cos_z = std::cos(deg_to_rad(pos.zenith_deg));
    const double ghi_direct = dni * cos_z;
    const double dhi = 0.1 * dni;
    const double ghi = ghi_direct + dhi;
    
    // Похила площина
    const double beta_rad = deg_to_rad(panel_tilt_deg);
    const double gamma_p_rad = deg_to_rad(panel_azimuth_deg);
    const double gamma_s_rad = deg_to_rad(pos.azimuth_deg);
    const double zenith_rad = deg_to_rad(pos.zenith_deg);
    
    double cos_theta = cos_z * std::cos(beta_rad) +
                       std::sin(zenith_rad) * std::sin(beta_rad) * std::cos(gamma_s_rad - gamma_p_rad);
    cos_theta = std::max(0.0, cos_theta);
    
    const double poa_direct = dni * cos_theta;
    const double poa_diffuse = dhi * (1.0 + std::cos(beta_rad)) / 2.0;
    const double poa_ground = ghi * albedo * (1.0 - std::cos(beta_rad)) / 2.0;
    
    const double poa_total = poa_direct + poa_diffuse + poa_ground;
    
    return IrradianceComponents{ghi, dni, dhi, poa_total};
}

int main() {
    const auto pos = calculate_solar_position(50.45, 30.52, 173, 10.0);
    const auto irr = calculate_irradiance(pos, 173, 35.0, 180.0);
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Зенітний кут: " << pos.zenith_deg << " deg | AM: " << pos.air_mass << "\n";
    std::cout << "DNI: " << irr.dni << " W/m2 | GHI: " << irr.ghi << " W/m2 | POA: " << irr.poa << " W/m2\n";
    return 0;
}
```
:::

### Інженерні особливості реалізації, крайові умови та оптимізація

1. **Захист від виходу за межі визначення тригонометричних функцій**:
   Під час арккосинусному обчисленні кутів значення `cos_zenith` та `cos_azimuth` через накопичення похибок плаваючої крапки можуть вийти за чисельний інтервал `[-1.0, 1.0]`. В обчислювальному коді застосовано обмеження `std::clamp(cos_val, -1.0, 1.0)` в C++ або `max(-1.0, min(1.0, val))` у Python. Це запобігає виклику `std::domain_error` або отриманню `NaN` у критичних моментах сходу й заходу Сонця.

2. **Запобігання від'ємним значенням інсоляції у нічний час**:
   У нічний час, коли Сонце перебуває нижче лінії горизонту (`elevation_deg <= 0`), пряме випромінювання `DNI` та кут падіння `cos(θ)` обнуляються. Функція `calculate_irradiance` перевіряє висоту Сонця і повертає нульові значення інсоляції, що унеможливлює від'ємний генераційний баланс у моделюванні фотоелектричних станцій.

3. **Практичне застосування на мікроконтролерах трекерних систем**:
   При впровадженні даного алгоритму в автономні контролери сонячного трекінгу (на базі мікроконтролерів STM32 чи ESP32):
   - Отримання поточного часу здійснюється від годинника реального часу `RTC` (наприклад, прецизійної мікросхеми DS3231 з температурною компенсацією кварцу);
   - Обчислення сонячних кутів `θ_z` та `γ_s` виконується кожні 1–5 хвилин для мінімізації енергоспоживання сервоприводів чи актуаторів;
   - Застосовується гібридне керування: алгоритмічний розрахунок сонячної позиції поєднується з давачами оптичного диференціального балансу (фотодіодними парами з перегородкою), що забезпечує точне донаведення навіть при мінливій хмарності.

4. **Аналіз обчислювальної складності та системна оптимізація**:
   Обчислення сонячної позиції для однієї часової мітки вимагає близько 12 викликів трансцендентних математичних функцій (`sin`, `cos`, `acos`, `pow`). На сучасних процесорах один такий виклик у C++ виконується за 15–20 наносекунд.
   
   При моделюванні великих сонячних парків із десятками тисяч окремо керованих трекерів або при річному моделюванні з інтервалом 1 секунда (31.5 мільйона обчислень) рекомендується:
   - Векторизувати обчислення за допомогою SIMD-інструкцій (AVX-512 або ARM Neon);
   - Використовувати апроксимацію `std::cos`/`std::sin` через поліноми Чебишова або табличні значення (Look-Up Tables, LUT);
   - Кешувати кути позиції Сонця `θ_z` та `γ_s` для всього масиву фотомодулів у даній географічній точці, здійснюючи лише векторний перерахунок `cos(θ)` для різних кутів нахилу `β` конкретних панелей.
