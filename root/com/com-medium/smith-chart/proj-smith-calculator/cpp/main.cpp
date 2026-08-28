// ============================================================================
// C++17/C++20 Implementation: Modern Smith Engine & Matching Solver
// ============================================================================
#include <iostream>
#include <complex>
#include <cmath>
#include <optional>
#include <numbers>
#include <iomanip>
#include <string_view>

namespace rf::smith {

enum class LMatchTopology {
    ParallelC_SeriesL,
    ParallelL_SeriesC,
    SeriesL_ParallelC,
    SeriesC_ParallelL
};

struct SmithPointMetrics {
    std::complex<double> z_raw;
    std::complex<double> z_norm;
    std::complex<double> gamma;
    double gamma_mag;
    double gamma_phase_deg;
    double vswr;
    double return_loss_db;
    double mismatch_loss_db;
};

struct LMatchSolution {
    LMatchTopology topology;
    double c_farads{0.0};
    double l_henries{0.0};
};

class Calculator {
public:
    [[nodiscard]] static SmithPointMetrics analyze(
        std::complex<double> z_load, double z0 = 50.0) noexcept 
    {
        if (z0 <= 0.0) z0 = 50.0;

        const std::complex<double> z_norm = z_load / z0;
        const std::complex<double> gamma = (z_norm - 1.0) / (z_norm + 1.0);
        const double mag = std::abs(gamma);
        const double phase_deg = std::arg(gamma) * 180.0 / std::numbers::pi;

        if (mag >= 0.9999) {
            return {z_load, z_norm, gamma, mag, phase_deg, 999.0, 0.0, 99.0};
        }

        const double vswr = (1.0 + mag) / (1.0 - mag);
        const double rl_db = -20.0 * std::log10(mag);
        const double ml_db = -10.0 * std::log10(1.0 - mag * mag);

        return {z_load, z_norm, gamma, mag, phase_deg, vswr, rl_db, ml_db};
    }

    [[nodiscard]] static std::optional<LMatchSolution> synthesize_lowpass_r_less(
        std::complex<double> z_load, double freq_hz, double z0 = 50.0) noexcept 
    {
        const double r_l = z_load.real();
        const double x_l = z_load.imag();
        const double omega = 2.0 * std::numbers::pi * freq_hz;

        if (r_l <= 0.0 || r_l >= z0 || omega <= 0.0) {
            return std::nullopt;
        }

        const double rad = r_l * (r_l * r_l + x_l * x_l - r_l * z0);
        if (rad < 0.0) {
            return std::nullopt;
        }

        const double b_p = (x_l + std::sqrt(r_l / z0) * std::sqrt(rad)) / (r_l * r_l + x_l * x_l);
        const double x_s = (1.0 / b_p) + (x_l * z0) / r_l - z0 / (b_p * r_l);

        if (b_p <= 0.0 || x_s <= 0.0) {
            return std::nullopt;
        }

        return LMatchSolution{
            LMatchTopology::ParallelC_SeriesL,
            b_p / omega,
            x_s / omega
        };
    }
};

void print_analysis(std::complex<double> z_load, double freq_hz, double z0 = 50.0) {
    const auto m = Calculator::analyze(z_load, z0);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "--- Звіт аналізу Smith Engine (C++17) ---\n";
    std::cout << "Частота:            " << freq_hz / 1e6 << " МГц\n";
    std::cout << "Імпеданс Z_L:       " << z_load.real() << " + j(" << z_load.imag() << ") Ом\n";
    std::cout << "Коефіцієнт Γ:       " << m.gamma.real() << " + j(" << m.gamma.imag() << ")\n";
    std::cout << "Модуль |Γ|:          " << m.gamma_mag << "\n";
    std::cout << "КСХ (VSWR):          " << std::setprecision(2) << m.vswr << " : 1\n";
    std::cout << "Return Loss:        " << m.return_loss_db << " дБ\n";

    if (const auto sol = Calculator::synthesize_lowpass_r_less(z_load, freq_hz, z0)) {
        std::cout << "L-Мережа (ФНЧ):      C = " << sol->c_farads * 1e12 << " пФ, L = "
                  << sol->l_henries * 1e9 << " нГн\n";
    }
    std::cout << "-----------------------------------------\n\n";
}

} // namespace rf::smith

int main() {
    rf::smith::print_analysis({25.0, 50.0}, 2.45e9);
    rf::smith::print_analysis({15.0, -30.0}, 868.0e6);
    return 0;
}
