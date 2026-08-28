#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>
#include <expected>
#include <string_view>

class ParabolicAntenna {
public:
    struct Config {
        double diameter_m{1.0};
        double freq_hz{10.0e9};
        double eta_aperture{0.65};
        double rms_surface_error_m{0.0005};
    };

    struct PerformanceMetrics {
        double wavelength_m;
        double aperture_area_m2;
        double effective_area_m2;
        double ideal_gain_dbi;
        double ruze_efficiency;
        double real_gain_dbi;
        double hpbw_degrees;
        double first_null_degrees;
    };

    explicit ParabolicAntenna(Config config) : config_(config) {}

    [[nodiscard]] std::expected<PerformanceMetrics, std::string_view> compute() const {
        if (config_.diameter_m <= 0.0 || config_.freq_hz <= 0.0) {
            return std::unexpected("Некоректні фізичні параметри антени");
        }

        constexpr double c = 299792458.0;
        const double lambda = c / config_.freq_hz;
        const double area = (std::numbers::pi * config_.diameter_m * config_.diameter_m) / 4.0;
        const double eff_area = config_.eta_aperture * area;

        const double directivity_iso = std::pow((std::numbers::pi * config_.diameter_m) / lambda, 2);
        const double ideal_gain_lin = config_.eta_aperture * directivity_iso;
        const double ideal_gain_dbi = 10.0 * std::log10(ideal_gain_lin);

        const double phase_error = (4.0 * std::numbers::pi * config_.rms_surface_error_m) / lambda;
        const double ruze_eff = std::exp(-std::pow(phase_error, 2));
        const double real_gain_dbi = ideal_gain_dbi + 10.0 * std::log10(ruze_eff);

        const double hpbw = 70.0 * (lambda / config_.diameter_m);
        const double null_angle = 1.22 * (lambda / config_.diameter_m) * (180.0 / std::numbers::pi);

        return PerformanceMetrics{
            .wavelength_m = lambda,
            .aperture_area_m2 = area,
            .effective_area_m2 = eff_area,
            .ideal_gain_dbi = ideal_gain_dbi,
            .ruze_efficiency = ruze_eff,
            .real_gain_dbi = real_gain_dbi,
            .hpbw_degrees = hpbw,
            .first_null_degrees = null_angle
        };
    }

    [[nodiscard]] double gain_at_angle(const PerformanceMetrics& metrics, double theta_deg) const {
        if (std::abs(theta_deg) < 1e-6) {
            return metrics.real_gain_dbi;
        }

        const double theta_rad = theta_deg * (std::numbers::pi / 180.0);
        const double u = (std::numbers::pi * config_.diameter_m / metrics.wavelength_m) * std::sin(theta_rad);

        const double field_norm = std::abs(2.0 * bessel_j1(u) / u);
        const double clamped_field = std::max(field_norm, 1e-4);

        return metrics.real_gain_dbi + 20.0 * std::log10(clamped_field);
    }

    struct PatternPoint {
        double angle_deg;
        double gain_dbi;
        double relative_db;
    };

    [[nodiscard]] std::vector<PatternPoint> generate_pattern(const PerformanceMetrics& metrics, 
                                                            double min_deg, double max_deg, double step_deg) const {
        std::vector<PatternPoint> pattern;
        for (double angle = min_deg; angle <= max_deg; angle += step_deg) {
            double g = gain_at_angle(metrics, angle);
            pattern.push_back({
                .angle_deg = angle,
                .gain_dbi = g,
                .relative_db = g - metrics.real_gain_dbi
            });
        }
        return pattern;
    }

private:
    Config config_;

    static double bessel_j1(double x) {
        const double ax = std::abs(x);
        if (ax < 3.75) {
            const double y = (x / 3.75) * (x / 3.75);
            return x * (0.5 + y * (-0.56249985 + y * (0.21093573 + y * (-0.03954289 + y * 0.00443319))));
        }
        const double y = 3.75 / ax;
        const double f1 = 0.79788456 + y * (-0.00000077 + y * (-0.00552740 + y * 0.00009512));
        const double theta1 = ax - 2.35619449 + y * (0.00000257 + y * (0.00552740 + y * (0.00009512)));
        return (1.0 / std::sqrt(ax)) * f1 * std::cos(theta1) * (x < 0 ? -1.0 : 1.0);
    }
};

int main() {
    ParabolicAntenna::Config cfg{
        .diameter_m = 1.2,
        .freq_hz = 12.0e9,
        .eta_aperture = 0.60,
        .rms_surface_error_m = 0.0008
    };

    ParabolicAntenna antenna(cfg);
    auto result = antenna.compute();

    if (!result) {
        std::cerr << "Помилка: " << result.error() << '\n';
        return 1;
    }

    const auto& metrics = *result;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ОБЧИСЛЕННЯ ПАРАМЕТРІВ ПАРАБОЛІЧНОЇ АНТЕНИ (C++) ===\n";
    std::cout << "Частота: " << cfg.freq_hz / 1e9 << " ГГц (λ = " << metrics.wavelength_m * 100.0 << " см)\n";
    std::cout << "Геометрична площа: " << metrics.aperture_area_m2 << " м²\n";
    std::cout << "Реальне підсилення (з формулою Рузе): " << metrics.real_gain_dbi << " dBi\n";
    std::cout << "Ефективність Рузе: " << metrics.ruze_efficiency * 100.0 << " %\n";
    std::cout << "Ширина променя HPBW: " << metrics.hpbw_degrees << "°\n\n";

    std::cout << "--- ЗРІЗ ДІАГРАМИ СПРЯМОВАНОСТІ ---\n";
    auto pattern = antenna.generate_pattern(metrics, -3.0, 3.0, 0.5);
    for (const auto& pt : pattern) {
        std::cout << "Кут " << std::setw(5) << pt.angle_deg << "° : " 
                  << std::setw(6) << pt.gain_dbi << " dBi  [" 
                  << std::setw(6) << pt.relative_db << " dB]\n";
    }

    return 0;
}
