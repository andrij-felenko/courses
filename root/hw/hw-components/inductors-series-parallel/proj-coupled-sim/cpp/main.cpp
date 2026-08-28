#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <iomanip>
#include <stdexcept>
#include <span>

namespace power_sim {

struct CircuitState {
    double i1{0.0};
    double i2{0.0};

    [[nodiscard]] constexpr double total_current() const noexcept { return i1 + i2; }
    [[nodiscard]] constexpr double circulating_current() const noexcept { return (i1 - i2) / 2.0; }
};

class CoupledInductorPair {
public:
    CoupledInductorPair(double l1, double l2, double k, double dcr1, double dcr2)
        : l1_{l1}, l2_{l2}, k_{k}, dcr1_{dcr1}, dcr2_{dcr2},
          m_{k * std::sqrt(l1 * l2)},
          det_l_{(l1 * l2) - (m_ * m_)} {
        if (det_l_ <= 0.0) {
            throw std::invalid_argument("Неприпустимий коефіцієнт зв'язку |k| >= 1.0 (det <= 0)");
        }
    }

    [[nodiscard]] std::pair<double, double> derivatives(const CircuitState& state,
                                                        double v1_ext, double v2_ext) const noexcept {
        const double v1_ind = v1_ext - (state.i1 * dcr1_);
        const double v2_ind = v2_ext - (state.i2 * dcr2_);

        const double di1 = (l2_ * v1_ind - m_ * v2_ind) / det_l_;
        const double di2 = (-m_ * v1_ind + l1_ * v2_ind) / det_l_;
        return {di1, di2};
    }

    [[nodiscard]] CircuitState rk4_step(const CircuitState& current,
                                        double v1_ext, double v2_ext, double dt) const noexcept {
        const auto [k1_1, k1_2] = derivatives(current, v1_ext, v2_ext);

        const CircuitState s2{
            current.i1 + 0.5 * dt * k1_1,
            current.i2 + 0.5 * dt * k1_2
        };
        const auto [k2_1, k2_2] = derivatives(s2, v1_ext, v2_ext);

        const CircuitState s3{
            current.i1 + 0.5 * dt * k2_1,
            current.i2 + 0.5 * dt * k2_2
        };
        const auto [k3_1, k3_2] = derivatives(s3, v1_ext, v2_ext);

        const CircuitState s4{
            current.i1 + dt * k3_1,
            current.i2 + dt * k3_2
        };
        const auto [k4_1, k4_2] = derivatives(s4, v1_ext, v2_ext);

        return {
            current.i1 + (dt / 6.0) * (k1_1 + 2.0 * k2_1 + 2.0 * k3_1 + k4_1),
            current.i2 + (dt / 6.0) * (k1_2 + 2.0 * k2_2 + 2.0 * k3_2 + k4_2)
        };
    }

    [[nodiscard]] double l1() const noexcept { return l1_; }
    [[nodiscard]] double l2() const noexcept { return l2_; }
    [[nodiscard]] double mutual_inductance() const noexcept { return m_; }
    [[nodiscard]] double coupling_factor() const noexcept { return k_; }

private:
    double l1_;
    double l2_;
    double k_;
    double dcr1_;
    double dcr2_;
    double m_;
    double det_l_;
};

} // namespace power_sim

int main() {
    using namespace power_sim;

    const double l_nominal = 150e-9; // 150 нГн
    const double k_coupling = -0.6;  // Інверсний зв'язок
    const double dcr = 0.001;        // 1 мОм

    CoupledInductorPair vrm_choke{l_nominal, l_nominal, k_coupling, dcr, dcr};

    CircuitState state{};
    constexpr double dt = 1e-9;          // 1 нс
    constexpr double t_total = 4e-6;     // 4 мкс
    constexpr double period = 2e-6;      // T = 2 мкс (500 кГц)
    constexpr double duty = 0.25;        // D = 0.25
    constexpr double vin = 12.0;         // Vin = 12 В
    constexpr double vout = 3.0;         // Vout = 3 В

    std::cout << "=== СИМУЛЯЦІЯ ДВОФАЗНОГО DC-DC ЗІ ЗВ'ЯЗАНИМ ДРОСЕЛЕМ (C++) ===\n";
    std::cout << "L = " << l_nominal * 1e9 << " нГн, k = " << k_coupling
              << ", DCR = " << dcr * 1000.0 << " мОм\n\n";

    std::cout << std::fixed << std::setprecision(3);
    std::cout << std::setw(10) << "Час [мкс]"
              << " | " << std::setw(12) << "Струм I1 [А]"
              << " | " << std::setw(12) << "Струм I2 [А]"
              << " | " << std::setw(14) << "Сумарний I [А]"
              << " | " << std::setw(16) << "Циркулюючий [А]\n";
    std::cout << std::string(76, '-') << "\n";

    for (double t = 0.0; t <= t_total; t += dt) {
        const double phase1_time = std::fmod(t, period);
        const double v1_sw = (phase1_time < (duty * period)) ? vin : 0.0;

        const double phase2_time = std::fmod(t + 0.5 * period, period);
        const double v2_sw = (phase2_time < (duty * period)) ? vin : 0.0;

        const double v1_ext = v1_sw - vout;
        const double v2_ext = v2_sw - vout;

        state = vrm_choke.rk4_step(state, v1_ext, v2_ext, dt);

        if (std::fmod(t + 1e-12, 200e-9) < dt) {
            std::cout << std::setw(10) << t * 1e6
                      << " | " << std::setw(12) << state.i1
                      << " | " << std::setw(12) << state.i2
                      << " | " << std::setw(14) << state.total_current()
                      << " | " << std::setw(16) << state.circulating_current() << "\n";
        }
    }

    return 0;
}
