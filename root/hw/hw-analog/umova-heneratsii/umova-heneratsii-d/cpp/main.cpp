#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <string_view>
#include <iomanip>

struct OscillatorParams {
    double frequency_hz{1000.0};
    double dt{1.0e-6};           // 1 мкс крок інтегрування
    double total_time_sec{0.025};// 25 мс
    double v_saturation{5.0};    // Напруга насичення рейок ОП (В)
    double small_signal_gain{3.40}; // Початковий коефіцієнт підсилення A_start
    double initial_noise_volts{10.0e-6}; // Тепловий поштовх 10 мкВ
};

class WienBridgeSimulator {
public:
    explicit WienBridgeSimulator(const OscillatorParams& params)
        : p_{params}, omega0_{2.0 * std::numbers::pi * params.frequency_hz} {}

    [[nodiscard]] double amplifier_nonlinearity(double v_in) const noexcept {
        return p_.v_saturation * std::tanh((p_.small_signal_gain * v_in) / p_.v_saturation);
    }

    void run_simulation() {
        double v_fb = p_.initial_noise_volts;
        double v_fb_dot = 0.0;
        double v_out = 0.0;

        const auto total_steps = static_cast<std::size_t>(p_.total_time_sec / p_.dt);
        const std::size_t print_interval = total_steps / 10;

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Час (мс) | V_вихід (В) | V_зз (В) | Режим генерації\n";
        std::cout << "--------------------------------------------------------\n";

        for (std::size_t step = 0; step < total_steps; ++step) {
            const double current_time_ms = static_cast<double>(step) * p_.dt * 1000.0;

            v_out = amplifier_nonlinearity(v_fb);

            // Диференціальний зв'язок моста Віна
            const double v_out_prev = amplifier_nonlinearity(v_fb - v_fb_dot * p_.dt);
            const double dv_out_dt = (step > 0) ? (v_out - v_out_prev) / p_.dt : 0.0;
            const double v_fb_ddot = omega0_ * dv_out_dt - 3.0 * omega0_ * v_fb_dot - omega0_ * omega0_ * v_fb;

            // Напівнеявне інтегрування
            v_fb_dot += v_fb_ddot * p_.dt;
            v_fb += v_fb_dot * p_.dt;

            if (step % print_interval == 0) {
                std::string_view status = "Експоненційне наростання";
                if (std::abs(v_out) > 4.5) {
                    status = "Стаціонарний (граничний цикл)";
                } else if (std::abs(v_out) > 0.5) {
                    status = "Нелінійна компресія підсилення";
                }

                std::cout << std::setw(8) << current_time_ms << " | "
                          << std::setw(11) << v_out << " | "
                          << std::setw(8) << v_fb << " | "
                          << status << '\n';
            }
        }
    }

private:
    OscillatorParams p_;
    double omega0_;
};

int main() {
    OscillatorParams config;
    WienBridgeSimulator simulator{config};
    simulator.run_simulation();
    return 0;
}
