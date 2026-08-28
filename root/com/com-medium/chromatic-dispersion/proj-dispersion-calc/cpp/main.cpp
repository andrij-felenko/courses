#include <iostream>
#include <cmath>
#include <expected>
#include <string_view>
#include <format>

namespace optical_network {

enum class CalculationError {
    InvalidWavelength,
    InvalidLength,
    ZeroDispersionCoefficients
};

struct FiberProfile {
    std::string_view name{"Generic SMF"};
    double zero_disp_wavelength_nm{1312.0};
    double zero_disp_slope{0.090};
    double attenuation_db_km{0.20};
};

struct LinkAnalysis {
    double dispersion_coeff_ps_nm_km{0.0};
    double accumulated_dispersion_ps_nm{0.0};
    double pulse_broadening_ps{0.0};
    double max_reach_km{0.0};
    bool requires_compensation{false};
};

class DispersionCalculator {
public:
    // Обчислення коефіцієнта D(λ) за формулою G.652
    [[nodiscard]] static constexpr double calculate_d(const FiberProfile& fiber, double wavelength_nm) noexcept {
        const double l0 = fiber.zero_disp_wavelength_nm;
        const double s0 = fiber.zero_disp_slope;
        const double l0_4_over_l3 = std::pow(l0, 4.0) / std::pow(wavelength_nm, 3.0);
        return (s0 / 4.0) * (wavelength_nm - l0_4_over_l3);
    }

    // Повний аналіз лінки
    [[nodiscard]] static std::expected<LinkAnalysis, CalculationError> analyze(
        const FiberProfile& fiber,
        double wavelength_nm,
        double link_length_km,
        double spectral_width_nm,
        double bit_rate_gbps,
        double max_cd_tolerance_ps_nm) noexcept 
    {
        if (wavelength_nm <= 0.0) return std::unexpected(CalculationError::InvalidWavelength);
        if (link_length_km <= 0.0) return std::unexpected(CalculationError::InvalidLength);

        const double d_coeff = calculate_d(fiber, wavelength_nm);
        const double accum_cd = d_coeff * link_length_km;
        const double broadening = std::abs(d_coeff) * spectral_width_nm * link_length_km;

        const double bit_period_ps = 1000.0 / bit_rate_gbps;
        const double max_allowed_broadening = 0.25 * bit_period_ps;

        double max_reach = 0.0;
        if (std::abs(d_coeff) > 1e-6 && spectral_width_nm > 1e-6) {
            max_reach = max_allowed_broadening / (std::abs(d_coeff) * spectral_width_nm);
        }

        return LinkAnalysis{
            .dispersion_coeff_ps_nm_km = d_coeff,
            .accumulated_dispersion_ps_nm = accum_cd,
            .pulse_broadening_ps = broadening,
            .max_reach_km = max_reach,
            .requires_compensation = (std::abs(accum_cd) > max_cd_tolerance_ps_nm)
        };
    }

    // Розрахунок довжини модуля DCF
    [[nodiscard]] static constexpr double calculate_dcf_length(double accum_cd_ps_nm, double dcf_d_coeff) noexcept {
        if (std::abs(dcf_d_coeff) < 1e-6) return 0.0;
        return -accum_cd_ps_nm / dcf_d_coeff;
    }
};

} // namespace optical_network

int main() {
    using namespace optical_network;

    constexpr FiberProfile smf28{
        .name = "Corning SMF-28e+",
        .zero_disp_wavelength_nm = 1312.0,
        .zero_disp_slope = 0.090,
        .attenuation_db_km = 0.19
    };

    constexpr double wavelength_nm = 1550.0;
    constexpr double length_km = 100.0;
    constexpr double spectral_width_nm = 0.1;
    constexpr double bit_rate_gbps = 10.0;
    constexpr double max_cd_tolerance = 800.0;

    auto result = DispersionCalculator::analyze(smf28, wavelength_nm, length_km, 
                                                 spectral_width_nm, bit_rate_gbps, max_cd_tolerance);

    if (result) {
        std::cout << std::format("=== Аналіз лінії {} (Довжина {} км) ===\n", smf28.name, length_km);
        std::cout << std::format("Коефіцієнт D(λ):          {:.2f} пс/(нм·км)\n", result->dispersion_coeff_ps_nm_km);
        std::cout << std::format("Накопичена дисперсія:     {:.1f} пс/нм\n", result->accumulated_dispersion_ps_nm);
        std::cout << std::format("Розширення імпульсу Δt:  {:.2f} пс\n", result->pulse_broadening_ps);
        std::cout << std::format("Максимальна досяжність:  {:.1f} км\n", result->max_reach_km);
        std::cout << std::format("Статус компенсації:      {}\n", 
                                 result->requires_compensation ? "ПОТРІБЕН МОДУЛЬ DCF" : "У МЕЖАХ ДОПУСКУ");

        if (result->requires_compensation) {
            constexpr double dcf_d = -120.0;
            double dcf_len = DispersionCalculator::calculate_dcf_length(result->accumulated_dispersion_ps_nm, dcf_d);
            std::cout << std::format("Необхідна катушка DCF:    {:.2f} км (при D = {:.1f} пс/(нм·км))\n", dcf_len, dcf_d);
        }
    } else {
        std::cerr << "Помилка розрахунку оптичної лінії!\n";
    }

    return 0;
}
