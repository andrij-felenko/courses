// main_igrf.cpp - C++ реалізація з еталонними викликами та перевіркою меж
#include <iostream>
#include <iomanip>
#include "igrf_model.hpp"

namespace geodynamo::igrf {

std::expected<MagneticVector, IGRFError> IGRFModel::evaluate(const GeodeticCoord& coord) const noexcept {
    if (coord.latitude_deg < -90.0 || coord.latitude_deg > 90.0) {
        return std::unexpected(IGRFError::InvalidLatitude);
    }
    if (coord.longitude_deg < -180.0 || coord.longitude_deg > 180.0) {
        return std::unexpected(IGRFError::InvalidLongitude);
    }

    const double lat_rad = coord.latitude_deg * (std::numbers::pi / 180.0);
    const double lon_rad = coord.longitude_deg * (std::numbers::pi / 180.0);
    const double colat = (90.0 - coord.latitude_deg) * (std::numbers::pi / 180.0);

    const double r = EarthRadiusKm + coord.altitude_km;
    const double r_ratio = EarthRadiusKm / r;
    const double r_factor = r_ratio * r_ratio * r_ratio;

    const double g10 = g_[1][0];
    const double g11 = g_[1][1];
    const double h11 = h_[1][1];

    const double Br = 2.0 * r_factor * (g10 * std::cos(colat) + (g11 * std::cos(lon_rad) + h11 * std::sin(lon_rad)) * std::sin(colat));
    const double Bt = -r_factor * (-g10 * std::sin(colat) + (g11 * std::cos(lon_rad) + h11 * std::sin(lon_rad)) * std::cos(colat));
    const double Bp = (r_factor / std::sin(colat)) * (-g11 * std::sin(lon_rad) + h11 * std::cos(lon_rad)) * std::sin(colat);

    MagneticVector res;
    res.X_nT = -Bt;
    res.Y_nT = Bp;
    res.Z_nT = -Br;
    res.H_nT = std::hypot(res.X_nT, res.Y_nT);
    res.F_nT = std::hypot(res.H_nT, res.Z_nT);
    res.D_deg = std::atan2(res.Y_nT, res.X_nT) * (180.0 / std::numbers::pi);
    res.I_deg = std::atan2(res.Z_nT, res.H_nT) * (180.0 / std::numbers::pi);

    return res;
}

} // namespace geodynamo::igrf

int main() {
    using namespace geodynamo::igrf;

    IGRFModel model;
    IGRFModel::Matrix g{}, h{};
    g[1][0] = -29400.0;
    g[1][1] = -1450.0;
    h[1][1] = 4650.0;
    model.set_coefficients(2025.0, g, h);

    GeodeticCoord coord{.latitude_deg = 50.4501, .longitude_deg = 30.5234, .altitude_km = 0.18, .epoch_year = 2025.0};

    auto result = model.evaluate(coord);
    if (result) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- C++ IGRF Результат (Київ 2025.0) ---\n";
        std::cout << "X (Північ): " << result->X_nT << " нТл\n";
        std::cout << "Y (Схід):   " << result->Y_nT << " нТл\n";
        std::cout << "Z (Вниз):   " << result->Z_nT << " нТл\n";
        std::cout << "H (Гориз):  " << result->H_nT << " нТл\n";
        std::cout << "F (Повне):  " << result->F_nT << " нТл\n";
        std::cout << "D (Деклін): " << result->D_deg << "°\n";
        std::cout << "I (Інклін): " << result->I_deg << "°\n";
    } else {
        std::cerr << "Помилка обчислення моделі IGRF!\n";
    }
    return 0;
}
