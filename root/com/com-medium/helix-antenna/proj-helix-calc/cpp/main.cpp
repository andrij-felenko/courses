#include <iostream>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <string_view>

struct HelixAntennaDesign {
    double freq_mhz;
    double lambda_mm;
    double diameter_mm;
    double spacing_mm;
    double total_length_mm;
    double wire_length_mm;
    double reflector_min_mm;
    double input_impedance_ohm;
    double gain_dbi;
    double hpbw_deg;
    double match_line_impedance_ohm;
};

enum class CalculationError {
    InvalidFrequency,
    InvalidTurnCount
};

constexpr std::string_view error_to_string(CalculationError err) noexcept {
    switch (err) {
        case CalculationError::InvalidFrequency: return "Частота повинна бути більшою за нуль";
        case CalculationError::InvalidTurnCount:  return "Кількість витків повинна бути від 3 до 30";
    }
    return "Невідома помилка";
}

[[nodiscard]] constexpr std::expected<HelixAntennaDesign, CalculationError>
design_helical_antenna(double freq_mhz, int num_turns) noexcept {
    if (freq_mhz <= 0.0) {
        return std::unexpected(CalculationError::InvalidFrequency);
    }
    if (num_turns < 3 || num_turns > 30) {
        return std::unexpected(CalculationError::InvalidTurnCount);
    }

    constexpr double speed_of_light_mm_s = 299792.458;
    const double lambda = speed_of_light_mm_s / freq_mhz;
    const double circumference = lambda; // C = lambda
    const double diameter = circumference / std::numbers::pi;

    // Pitch angle alpha = 12.8 degrees
    constexpr double pitch_angle_rad = 12.8 * std::numbers::pi / 180.0;
    const double spacing = circumference * std::tan(pitch_angle_rad);

    const double turn_length = std::hypot(circumference, spacing);
    const double total_length = num_turns * spacing;
    const double wire_length = num_turns * turn_length;
    const double reflector_dim = 0.75 * lambda;

    const double c_rel = circumference / lambda;
    const double s_rel = spacing / lambda;

    const double r_in = 140.0 * c_rel;
    const double g_lin = 12.0 * num_turns * (c_rel * c_rel) * s_rel;
    const double gain = 10.0 * std::log10(g_lin);

    const double hpbw = 52.0 / (c_rel * std::sqrt(num_turns * s_rel));
    const double z_match = std::sqrt(50.0 * r_in);

    return HelixAntennaDesign{
        .freq_mhz = freq_mhz,
        .lambda_mm = lambda,
        .diameter_mm = diameter,
        .spacing_mm = spacing,
        .total_length_mm = total_length,
        .wire_length_mm = wire_length,
        .reflector_min_mm = reflector_dim,
        .input_impedance_ohm = r_in,
        .gain_dbi = gain,
        .hpbw_deg = hpbw,
        .match_line_impedance_ohm = z_match
    };
}

int main() {
    constexpr double target_freq = 2437.0; // Wi-Fi / Bluetooth
    constexpr int turns_count = 8;

    const auto result = design_helical_antenna(target_freq, turns_count);

    if (!result) {
        std::cerr << "Помилка розрахунку: " << error_to_string(result.error()) << '\n';
        return 1;
    }

    const auto& h = *result;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Розрахунок спіральної антени (C++17/23) ===\n"
              << "Частота:                  " << h.freq_mhz << " МГц (λ = " << h.lambda_mm << " мм)\n"
              << "Кількість витків N:        " << turns_count << "\n"
              << "Діаметр спіралі D:        " << h.diameter_mm << " мм\n"
              << "Крок витка S:             " << h.spacing_mm << " мм\n"
              << "Осьова довжина L:         " << h.total_length_mm << " мм\n"
              << "Загальна довжина дроту:   " << h.wire_length_mm << " мм\n"
              << "Розмір рефлектора D_gp:   >= " << h.reflector_min_mm << " мм\n"
              << "-------------------------------------------\n"
              << "Вхідний опір R_in:        " << h.input_impedance_ohm << " Ом\n"
              << "Трансформатор до 50 Ом:   Z0 = " << h.match_line_impedance_ohm 
              << " Ом (L = " << (h.lambda_mm / 4.0) << " мм)\n"
              << "Коефіцієнт підсилення:     " << h.gain_dbi << " дБі\n"
              << "Ширина променя (HPBW):    " << h.hpbw_deg << " градусів\n";

    return 0;
}
