#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <algorithm>
#include <expected>
#include <string_view>
#include <iomanip>

namespace rf {

inline constexpr double Z0 = 50.0;

struct ComplexZ {
    double r{0.0};  // активний опір (Ом)
    double x{0.0};  // реактивний опір (Ом)
};

struct MatchingResult {
    double c_shunt_pf{0.0};
    double l_series_nh{0.0};
    double c_real_pf{0.0};
    double l_real_nh{0.0};
    double vswr_real{1.0};
    double s11_db_real{-100.0};
    double refl_power_pct{0.0};
};

enum class MatchingError {
    InvalidResistance,
    TopologyNotSupported
};

// Стандартний ряд номіналів E24
inline constexpr std::array<double, 24> E24_VALUES = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

constexpr double quantize_to_e24(double val) noexcept {
    if (val <= 0.0) return 0.0;
    const double exponent = std::floor(std::log10(val));
    const double mantissa = val / std::pow(10.0, exponent);
    
    auto it = std::min_element(E24_VALUES.begin(), E24_VALUES.end(),
        [mantissa](double a, double b) {
            return std::abs(mantissa - a) < std::abs(mantissa - b);
        });
    return *it * std::pow(10.0, exponent);
}

double calculate_vswr(const ComplexZ& z, double& out_s11_db) noexcept {
    const double num_mag = std::hypot(z.r - Z0, z.x);
    const double den_mag = std::hypot(z.r + Z0, z.x);
    if (den_mag == 0.0) return 999.0;
    
    double gamma = std::clamp(num_mag / den_mag, 0.0, 0.9999);
    out_s11_db = (gamma > 1e-6) ? (20.0 * std::log10(gamma)) : -120.0;
    return (1.0 + gamma) / (1.0 - gamma);
}

// Розрахунок L-ланки для імпедансу антени R_L < 50 Ом
std::expected<MatchingResult, MatchingError> calculate_l_match(
    double freq_hz, const ComplexZ& z_ant) noexcept 
{
    if (z_ant.r <= 0.0) return std::unexpected(MatchingError::InvalidResistance);
    if (z_ant.r >= Z0) return std::unexpected(MatchingError::TopologyNotSupported);
    
    const double w = 2.0 * std::numbers::pi * freq_hz;
    
    // 1. Теоретичний розрахунок L-ланки
    const double q = std::sqrt((Z0 / z_ant.r) - 1.0);
    const double b_shunt = q / Z0;
    const double x_series = (q * z_ant.r) - z_ant.x;
    
    MatchingResult res{};
    res.c_shunt_pf = (b_shunt / w) * 1e12;
    res.l_series_nh = (x_series / w) * 1e9;
    
    // 2. Квантування до ряду E24
    res.c_real_pf = quantize_to_e24(res.c_shunt_pf);
    res.l_real_nh = quantize_to_e24(res.l_series_nh);
    
    // 3. Пряме моделювання вхідного імпедансу
    const double c_farads = res.c_real_pf * 1e-12;
    const double l_henries = res.l_real_nh * 1e-9;
    
    // Z1 = Z_ant + j*w*L
    const double z1_r = z_ant.r;
    const double z1_x = z_ant.x + (w * l_henries);
    
    // Y1 = 1 / Z1
    const double denom1 = z1_r * z1_r + z1_x * z1_x;
    const double y1_g = z1_r / denom1;
    const double y1_b = -z1_x / denom1;
    
    // Yin = Y1 + j*w*C
    const double yin_g = y1_g;
    const double yin_b = y1_b + (w * c_farads);
    
    // Zin = 1 / Yin
    const double denom_in = yin_g * yin_g + yin_b * yin_b;
    const ComplexZ z_in{
        .r = yin_g / denom_in,
        .x = -yin_b / denom_in
    };
    
    res.vswr_real = calculate_vswr(z_in, res.s11_db_real);
    const double gamma_real = (res.vswr_real - 1.0) / (res.vswr_real + 1.0);
    res.refl_power_pct = gamma_real * gamma_real * 100.0;
    
    return res;
}

} // namespace rf

int main() {
    constexpr double freq = 2.44e9;
    constexpr rf::ComplexZ z_detuned{.r = 15.0, .x = -35.0};
    
    auto match = rf::calculate_l_match(freq, z_detuned);
    if (match.has_value()) {
        const auto& res = match.value();
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- Узгодження антени 2.44 ГГц (C++) ---\n";
        std::cout << "Вхідний імпеданс антени: " << z_detuned.r << " + j(" << z_detuned.x << ") Ом\n";
        std::cout << "Теоретичні номінали: C_shunt = " << res.c_shunt_pf << " пФ, L_series = " << res.l_series_nh << " нГн\n";
        std::cout << "Реальні номінали E24:  C = " << res.c_real_pf << " пФ, L = " << res.l_real_nh << " нГн\n";
        std::cout << "Фактичний КСВ з E24:   " << res.vswr_real << " (S11 = " << res.s11_db_real 
                  << " дБ, відбито " << res.refl_power_pct << "% потужності)\n";
    }
    return 0;
}
