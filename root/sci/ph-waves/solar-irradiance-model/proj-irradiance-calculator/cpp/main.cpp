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
