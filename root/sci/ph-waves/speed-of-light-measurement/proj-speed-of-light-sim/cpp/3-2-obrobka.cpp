#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct LidarConfig {
    double mod_freq_hz{50000000.0}; // 50 МГц
    double true_distance_m{15.45};
    double speed_of_light{299792458.0};
};

class PhaseLidarProcessor {
public:
    explicit PhaseLidarProcessor(LidarConfig cfg) : cfg_(cfg) {}

    [[nodiscard]] std::pair<double, double> process(std::size_t sample_count = 1000) const {
        const double t_flight = 2.0 * cfg_.true_distance_m / cfg_.speed_of_light;
        const double phase_true = 2.0 * std::numbers::pi * cfg_.mod_freq_hz * t_flight;

        std::vector<double> ref(sample_count);
        std::vector<double> meas(sample_count);

        for (std::size_t i = 0; i < sample_count; ++i) {
            const double t = static_cast<double>(i) / (static_cast<double>(sample_count) * cfg_.mod_freq_hz);
            ref[i] = std::cos(2.0 * std::numbers::pi * cfg_.mod_freq_hz * t);
            meas[i] = std::cos(2.0 * std::numbers::pi * cfg_.mod_freq_hz * t - phase_true);
        }

        double I_comp = 0.0;
        double Q_comp = 0.0;
        for (std::size_t i = 0; i < sample_count; ++i) {
            I_comp += meas[i] * ref[i];
            Q_comp += meas[i] * std::sin(2.0 * std::numbers::pi * static_cast<double>(i) / static_cast<double>(sample_count));
        }

        double delta_phi = std::atan2(Q_comp, I_comp);
        if (delta_phi < 0.0) delta_phi += 2.0 * std::numbers::pi;

        const double distance_est = (cfg_.speed_of_light * delta_phi) / (4.0 * std::numbers::pi * cfg_.mod_freq_hz);
        return {delta_phi, distance_est};
    }

private:
    LidarConfig cfg_;
};

int main() {
    LidarConfig cfg{.mod_freq_hz = 50000000.0, .true_distance_m = 15.45, .speed_of_light = 299792458.0};
    PhaseLidarProcessor lidar(cfg);

    auto [phase_rad, distance_m] = lidar.process(1000);

    std::cout << "=== Обробка фазового далекоміра LiDAR (C++) ===\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Задана відстань: " << cfg.true_distance_m << " м\n";
    std::cout << "Фазовий зсув: " << phase_rad << " рад\n";
    std::cout << "Відновлена відстань: " << distance_m << " м\n";
    std::cout << "Нев'язка: " << (std::abs(distance_m - cfg.true_distance_m) * 1000.0) << " мм\n";

    return 0;
}
