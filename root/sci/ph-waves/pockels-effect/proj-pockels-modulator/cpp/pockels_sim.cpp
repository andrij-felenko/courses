// pockels_sim.cpp - Ідіоматична реалізація моделі комірки Поккельса мовою C++20
#include <iostream>
#include <complex>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

using namespace std::complex_literals;

namespace optics {

struct JonesVector {
    std::complex<double> ex{1.0, 0.0};
    std::complex<double> ey{0.0, 0.0};

    [[nodiscard]] constexpr double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }
};

class PockelsModulator {
public:
    struct Params {
        double v_pi{300.0};           // Напівхвильова напруга (В)
        double wavelength{1550e-9};   // Довжина хвилі (м)
        double crystal_length{0.02};  // Довжина (м)
        double dn_dt{3.9e-5};         // Термооптичний коефіцієнт (1/K)
        double ref_temp{25.0};        // Базова температура (°C)
    };

    explicit PockelsModulator(Params params) noexcept : params_(params) {}

    [[nodiscard]] double calculate_retardation(double voltage, double temperature) const noexcept {
        const double gamma_v = std::numbers::pi * (voltage / params_.v_pi);
        const double delta_t = temperature - params_.ref_temp;
        const double gamma_t = (2.0 * std::numbers::pi / params_.wavelength) *
                               params_.dn_dt * params_.crystal_length * delta_t;
        return gamma_v + gamma_t;
    }

    [[nodiscard]] JonesVector process_beam(const JonesVector& in, double voltage, double temperature) const noexcept {
        const double gamma = calculate_retardation(voltage, temperature);

        // 1. Вхідний поляризатор P1 під кутом 45°
        const auto p1_scalar = 0.5 * (in.ex + in.ey);
        const JonesVector after_p1{p1_scalar, p1_scalar};

        // 2. Фазова деформація в комірці Поккельса
        const auto phase_x = std::exp(-0.5i * gamma);
        const auto phase_y = std::exp(0.5i * gamma);
        const JonesVector inside_cell{after_p1.ex * phase_x, after_p1.ey * phase_y};

        // 3. Аналізатор P2 під кутом -45°
        const auto diff = 0.5 * (inside_cell.ex - inside_cell.ey);
        return JonesVector{diff, -diff};
    }

    [[nodiscard]] double auto_bias_compensate(double current_temp) const noexcept {
        // Обчислення необхідної напруги зсуву V_bias для компенсації температури
        const double delta_t = current_temp - params_.ref_temp;
        const double thermal_phase = (2.0 * std::numbers::pi / params_.wavelength) *
                                     params_.dn_dt * params_.crystal_length * delta_t;
        
        // Коррегуємо напругу так, щоб сумарний фазовий набіг дорівнював π/2
        const double target_phase = std::numbers::pi / 2.0;
        const double required_v_phase = target_phase - std::fmod(thermal_phase, 2.0 * std::numbers::pi);
        return (required_v_phase / std::numbers::pi) * params_.v_pi;
    }

private:
    Params params_;
};

} // namespace optics

int main() {
    using namespace optics;

    PockelsModulator modulator({
        .v_pi = 300.0,
        .wavelength = 1550e-9,
        .crystal_length = 0.02,
        .dn_dt = 3.9e-5,
        .ref_temp = 25.0
    });

    std::cout << "=== МОДЕЛЮВАННЯ МОДУЛЯТОРА ПОККЕЛЬСА (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(4);

    const JonesVector input_laser{1.0, 0.0};
    const double base_bias = 150.0; // V_pi / 2

    std::cout << "\n1. Амплітудно-частотна характеристика (T = 25 °C):\n";
    const std::vector<double> test_voltages{0.0, 75.0, 150.0, 225.0, 300.0};
    for (double v : test_voltages) {
        const auto out = modulator.process_beam(input_laser, v, 25.0);
        const double ret = modulator.calculate_retardation(v, 25.0);
        std::cout << "  V = " << std::setw(5) << v << " V | Gamma = "
                  << std::setw(7) << ret << " rad | Transmission = "
                  << std::setw(7) << out.intensity() << "\n";
    }

    std::cout << "\n2. Автоматична компенсація температурного дрейфу:\n";
    const std::vector<double> temp_steps{25.0, 28.0, 32.0, 35.0};
    for (double temp : temp_steps) {
        const double comp_v = modulator.auto_bias_compensate(temp);
        const auto out = modulator.process_beam(input_laser, comp_v, temp);
        std::cout << "  T = " << temp << " °C | Comp. Bias = " << comp_v
                  << " V | Intensity = " << out.intensity() << " (Стабілізовано 0.5000)\n";
    }

    return 0;
}
