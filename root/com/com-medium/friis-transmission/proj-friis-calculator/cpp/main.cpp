#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

namespace rf {

constexpr double SPEED_OF_LIGHT = 299'792'458.0;

enum class LinkError {
    InvalidFrequency,
    InvalidDistance,
    NearFieldViolation
};

struct LinkParameters {
    double tx_power_dbm{0.0};
    double tx_gain_dbi{0.0};
    double rx_gain_dbi{0.0};
    double frequency_hz{2.4e9};
    double distance_m{1.0};
    double rx_sensitivity_dbm{-90.0};
    double system_loss_db{0.0};
    double antenna_aperture_m{0.0};
};

struct LinkAnalysis {
    double wavelength_m{0.0};
    double eirp_dbm{0.0};
    double fspl_db{0.0};
    double rx_power_dbm{0.0};
    double rx_power_mw{0.0};
    double link_margin_db{0.0};
    double far_field_boundary_m{0.0};
    bool in_far_field{true};
    bool is_viable{false};
};

class FriisCalculator {
public:
    [[nodiscard]] static constexpr double wavelength(double freq_hz) noexcept {
        return SPEED_OF_LIGHT / freq_hz;
    }

    [[nodiscard]] static double fspl(double freq_hz, double distance_m) noexcept {
        const double lambda = wavelength(freq_hz);
        const double ratio = (4.0 * std::numbers::pi * distance_m) / lambda;
        return 20.0 * std::log10(ratio);
    }

    [[nodiscard]] static double far_field_distance(double aperture_m, double freq_hz) noexcept {
        const double lambda = wavelength(freq_hz);
        return (2.0 * aperture_m * aperture_m) / lambda;
    }

    [[nodiscard]] static std::expected<LinkAnalysis, LinkError> analyze(const LinkParameters& p) noexcept {
        if (p.frequency_hz <= 0.0) {
            return std::unexpected(LinkError::InvalidFrequency);
        }
        if (p.distance_m <= 0.0) {
            return std::unexpected(LinkError::InvalidDistance);
        }

        LinkAnalysis res;
        res.wavelength_m = wavelength(p.frequency_hz);
        res.eirp_dbm = p.tx_power_dbm + p.tx_gain_dbi;
        res.fspl_db = fspl(p.frequency_hz, p.distance_m);
        res.rx_power_dbm = res.eirp_dbm + p.rx_gain_dbi - res.fspl_db - p.system_loss_db;
        res.rx_power_mw = std::pow(10.0, res.rx_power_dbm / 10.0);
        res.link_margin_db = res.rx_power_dbm - p.rx_sensitivity_dbm;
        res.is_viable = (res.link_margin_db >= 0.0);

        if (p.antenna_aperture_m > 0.0) {
            res.far_field_boundary_m = far_field_distance(p.antenna_aperture_m, p.frequency_hz);
            res.in_far_field = (p.distance_m >= res.far_field_boundary_m);
        }

        return res;
    }
};

} // namespace rf

int main() {
    rf::LinkParameters params{
        .tx_power_dbm = 14.0,
        .tx_gain_dbi = 3.0,
        .rx_gain_dbi = 3.0,
        .frequency_hz = 2.4e9,
        .distance_m = 500.0,
        .rx_sensitivity_dbm = -95.0,
        .system_loss_db = 2.0,
        .antenna_aperture_m = 0.12
    };

    auto result = rf::FriisCalculator::analyze(params);

    if (result) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== ОБЧИСЛЕННЯ ЛІНКА ЗА ФРІЇСОМ (C++) ===\n";
        std::cout << "Довжина хвилі:      " << result->wavelength_m << " м\n";
        std::cout << "Втрати FSPL:        " << result->fspl_db << " дБ\n";
        std::cout << "Прийнята потужність: " << result->rx_power_dbm << " дБм\n";
        std::cout << "Запас лінка:        " << result->link_margin_db << " дБ ("
                  << (result->is_viable ? "ПРАЦЮЄ" : "ВТРАТА ЗВ'ЯЗКУ") << ")\n";
        std::cout << "Межа дальньої зони: " << result->far_field_boundary_m << " м ("
                  << (result->in_far_field ? "ДАЛЬНЯ ЗОНА" : "ПОМИЛКА: БЛИЖНЯ ЗОНА") << ")\n";
    } else {
        std::cerr << "Помилка розрахунку лінка!\n";
    }

    return 0;
}
