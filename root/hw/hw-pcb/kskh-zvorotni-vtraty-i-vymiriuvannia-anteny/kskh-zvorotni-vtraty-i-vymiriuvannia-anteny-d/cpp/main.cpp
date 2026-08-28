#include <complex>
#include <numbers>
#include <cmath>
#include <optional>
#include <format>
#include <iostream>

struct RfMetrics {
    double vswr;
    double gamma_mag;
    double gamma_phase_deg;
    double return_loss_db;
    double mismatch_loss_db;
    double radiated_power_percent;
};

struct LMatchResult {
    bool series_first; // true: послідовна L до антени, паралельна C
    double l_val_nh;
    double c_val_pf;
    double q_factor;
};

class AntennaMatcher {
public:
    static constexpr double PI = std::numbers::pi;

    static RfMetrics calculate_metrics(std::complex<double> z_load, double z0 = 50.0) noexcept {
        const std::complex<double> gamma = (z_load - z0) / (z_load + z0);
        const double gamma_mag = std::abs(gamma);
        const double gamma_phase_deg = std::arg(gamma) * (180.0 / PI);

        if (gamma_mag >= 1.0) {
            return {
                .vswr = 999.99,
                .gamma_mag = gamma_mag,
                .gamma_phase_deg = gamma_phase_deg,
                .return_loss_db = 0.0,
                .mismatch_loss_db = 999.99,
                .radiated_power_percent = 0.0
            };
        }

        const double vswr = (1.0 + gamma_mag) / (1.0 - gamma_mag);
        const double return_loss = -20.0 * std::log10(std::max(gamma_mag, 1e-6));
        const double p_trans = 1.0 - (gamma_mag * gamma_mag);
        const double mismatch_loss = -10.0 * std::log10(std::max(p_trans, 1e-6));

        return {
            .vswr = vswr,
            .gamma_mag = gamma_mag,
            .gamma_phase_deg = gamma_phase_deg,
            .return_loss_db = return_loss,
            .mismatch_loss_db = mismatch_loss,
            .radiated_power_percent = p_trans * 100.0
        };
    }

    static std::optional<LMatchResult> synthesize_l_match(
        std::complex<double> z_load, 
        double freq_hz, 
        double z0 = 50.0) noexcept 
    {
        const double r_a = z_load.real();
        const double x_a = z_load.imag();
        const double omega = 2.0 * PI * freq_hz;

        if (r_a <= 0.0 || freq_hz <= 0.0 || z0 <= 0.0) {
            return std::nullopt;
        }

        if (r_a < z0) {
            const double q = std::sqrt((z0 / r_a) - 1.0);
            const double x_s = (q * r_a) - x_a;
            const double b_p = q / z0;

            return LMatchResult{
                .series_first = true,
                .l_val_nh = (x_s / omega) * 1e9,
                .c_val_pf = (b_p / omega) * 1e12,
                .q_factor = q
            };
        } else {
            const double q = std::sqrt((r_a / z0) - 1.0);
            const double b_p = q / r_a;
            const double x_s = (q * z0) - x_a;

            return LMatchResult{
                .series_first = false,
                .l_val_nh = (x_s / omega) * 1e9,
                .c_val_pf = (b_p / omega) * 1e12,
                .q_factor = q
            };
        }
    }
};
