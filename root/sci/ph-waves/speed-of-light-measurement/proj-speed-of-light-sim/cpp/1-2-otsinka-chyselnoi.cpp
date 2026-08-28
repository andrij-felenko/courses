#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct FizeauSetup {
    double base_length_m{8633.0};
    int num_teeth{720};
    double speed_of_light{299792458.0};
};

class FizeauSimulator {
public:
    explicit FizeauSimulator(FizeauSetup setup) : setup_(setup) {}

    [[nodiscard]] double compute_transmission(double t, double freq_hz) const noexcept {
        const double period = 1.0 / (setup_.num_teeth * freq_hz);
        double phase = std::fmod(t, period);
        if (phase < 0.0) phase += period;
        return (phase < (period * 0.5)) ? 1.0 : 0.0;
    }

    [[nodiscard]] double calculate_intensity(double freq_hz, std::size_t samples = 1000) const {
        const double t_flight = 2.0 * setup_.base_length_m / setup_.speed_of_light;
        const double period = 1.0 / (setup_.num_teeth * freq_hz);
        const double dt = period / static_cast<double>(samples);

        double sum_intensity = 0.0;
        for (std::size_t i = 0; i < samples; ++i) {
            const double t_emit = static_cast<double>(i) * dt;
            const double t_recv = t_emit + t_flight;
            const double t_in = compute_transmission(t_emit, freq_hz);
            const double t_out = compute_transmission(t_recv, freq_hz);
            sum_intensity += (t_in * t_out);
        }
        return sum_intensity / static_cast<double>(samples);
    }

    [[nodiscard]] double estimate_speed_of_light(double eclipse_freq_hz) const noexcept {
        return 4.0 * setup_.num_teeth * setup_.base_length_m * eclipse_freq_hz;
    }

private:
    FizeauSetup setup_;
};

int main() {
    FizeauSetup config{.base_length_m = 8633.0, .num_teeth = 720, .speed_of_light = 299792458.0};
    FizeauSimulator sim(config);

    std::cout << "=== Симуляція експерименту Фізо (C++) ===\n";
    std::cout << std::fixed << std::setprecision(2);

    double min_intensity = 1.0;
    double min_freq = 0.0;

    for (double f = 1.0; f <= 25.0; f += 0.05) {
        double intensity = sim.calculate_intensity(f);
        if (intensity < min_intensity) {
            min_intensity = intensity;
            min_freq = f;
        }
    }

    double c_estimated = sim.estimate_speed_of_light(min_freq);
    std::cout << "Перше затемнення на частоті: " << min_freq << " Гц\n";
    std::cout << "Обчислена швидкість світла: " << (c_estimated / 1000.0) << " км/с\n";
    std::cout << "Відносна похибка: " 
              << (std::abs(c_estimated - config.speed_of_light) / config.speed_of_light * 100.0) << "%\n";

    return 0;
}
