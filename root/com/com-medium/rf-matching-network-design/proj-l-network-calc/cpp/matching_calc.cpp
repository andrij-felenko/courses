// cpp/matching_calc.cpp — Ідіоматичний калькулятор та симулятор L-ланок на C++20
#include <iostream>
#include <complex>
#include <vector>
#include <numbers>
#include <cmath>
#include <expected>
#include <iomanip>

namespace rf {

enum class Topology {
    LowpassStepDown,
    LowpassStepUp,
    HighpassStepDown,
    HighpassStepUp
};

struct MatchingNetwork {
    Topology type;
    double inductance_H;
    double capacitance_F;
    double quality_factor;
};

enum class MathError {
    InvalidImpedance,
    InvalidFrequency,
    NegativeDiscriminant
};

// Обчислення L-ланки з використанням std::expected (C++23 / fallback pattern)
class MatchingCalculator {
public:
    static std::expected<MatchingNetwork, MathError>
    calculate_l_network(double R_source, double R_load, double freq_hz, bool lowpass = true) noexcept {
        if (R_source <= 0.0 || R_load <= 0.0) {
            return std::unexpected(MathError::InvalidImpedance);
        }
        if (freq_hz <= 0.0) {
            return std::unexpected(MathError::InvalidFrequency);
        }

        const double omega0 = 2.0 * std::numbers::pi * freq_hz;
        const double R_high = std::max(R_source, R_load);
        const double R_low  = std::min(R_source, R_load);

        const double Q_sq = (R_high / R_low) - 1.0;
        if (Q_sq < 0.0) {
            return std::unexpected(MathError::NegativeDiscriminant);
        }

        const double Q = std::sqrt(Q_sq);
        const double X_series   = Q * R_low;
        const double X_parallel = R_high / Q;

        MatchingNetwork result{};
        result.quality_factor = Q;

        if (R_source > R_load) {
            if (lowpass) {
                result.type = Topology::LowpassStepDown;
                result.capacitance_F = 1.0 / (omega0 * X_parallel);
                result.inductance_H  = X_series / omega0;
            } else {
                result.type = Topology::HighpassStepDown;
                result.inductance_H  = X_parallel / omega0;
                result.capacitance_F = 1.0 / (omega0 * X_series);
            }
        } else {
            if (lowpass) {
                result.type = Topology::LowpassStepUp;
                result.inductance_H  = X_series / omega0;
                result.capacitance_F = 1.0 / (omega0 * X_parallel);
            } else {
                result.type = Topology::HighpassStepUp;
                result.capacitance_F = 1.0 / (omega0 * X_series);
                result.inductance_H  = X_parallel / omega0;
            }
        }

        return result;
    }
};

struct SweepPoint {
    double frequency_hz;
    std::complex<double> input_impedance;
    double reflection_coeff;
    double vswr;
};

// Симулятор частотного аналізу
class FrequencySimulator {
public:
    static std::vector<SweepPoint>
    simulate_lowpass_step_up(double R_source, double R_load, const MatchingNetwork& net,
                             double f_start_hz, double f_end_hz, size_t steps,
                             double Q_inductor = 100.0) {
        std::vector<SweepPoint> results;
        results.reserve(steps);

        const double step_size = (f_end_hz - f_start_hz) / static_cast<double>(steps - 1);

        for (size_t i = 0; i < steps; ++i) {
            const double f = f_start_hz + static_cast<double>(i) * step_size;
            const double omega = 2.0 * std::numbers::pi * f;

            // Паралельне з'єднання R_load та C
            const std::complex<double> Z_load{R_load, 0.0};
            const std::complex<double> Z_cap{0.0, -1.0 / (omega * net.capacitance_F)};
            const std::complex<double> Z_parallel = (Z_load * Z_cap) / (Z_load + Z_cap);

            // Послідовна індуктивність із урахуванням втрат R_ESR
            const double R_esr = (Q_inductor > 0.0) ? (omega * net.inductance_H / Q_inductor) : 0.0;
            const std::complex<double> Z_ind{R_esr, omega * net.inductance_H};

            const std::complex<double> Z_in = Z_parallel + Z_ind;

            // S11 відносно R_source
            const std::complex<double> S11 = (Z_in - R_source) / (Z_in + R_source);
            const double gamma = std::abs(S11);
            const double vswr = (gamma >= 0.999) ? 99.9 : ((1.0 + gamma) / (1.0 - gamma));

            results.push_back({f, Z_in, gamma, vswr});
        }

        return results;
    }
};

} // namespace rf

int main() {
    constexpr double R_S = 10.0;      // Опір підсилювача (10 Ом)
    constexpr double R_L = 50.0;      // Опір антени (50 Ом)
    constexpr double f0  = 433.92e6;  // Частота 433.92 МГц

    std::cout << "=== ІДІОМАТИЧНИЙ СИМУЛЯТОР L-ЛАНОК (C++20/C++23) ===\n";

    auto net_opt = rf::MatchingCalculator::calculate_l_network(R_S, R_L, f0, true);

    if (!net_opt) {
        std::cerr << "Помилка обчислення узгодження!\n";
        return 1;
    }

    const auto& net = *net_opt;
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Розраховані параметри L-ланки:\n"
              << "  Q добротність = " << net.quality_factor << "\n"
              << "  L індуктивність = " << net.inductance_H * 1e9 << " нГн\n"
              << "  C ємність       = " << net.capacitance_F * 1e12 << " пФ\n\n";

    auto sweep = rf::FrequencySimulator::simulate_lowpass_step_up(R_S, R_L, net, f0 * 0.8, f0 * 1.2, 9, 80.0);

    std::cout << "--- РЕЗУЛЬТАТИ СИМУЛЯЦІЇ (Sweep 347 МГц .. 520 МГц) ---\n";
    std::cout << "Частота (МГц) | Zin (Ом)             | |S11|   |  КСХ (VSWR)\n";
    std::cout << "--------------+----------------------+---------+-------------\n";

    for (const auto& pt : sweep) {
        std::cout << std::setw(13) << pt.frequency_hz / 1e6 << " | "
                  << std::setw(6) << pt.input_impedance.real() << " + j"
                  << std::setw(6) << pt.input_impedance.imag() << " | "
                  << std::setw(7) << pt.reflection_coeff << " | "
                  << std::setw(11) << pt.vswr << "\n";
    }

    return 0;
}
