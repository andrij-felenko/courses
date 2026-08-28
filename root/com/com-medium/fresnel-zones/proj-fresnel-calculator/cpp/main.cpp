#include <iostream>
#include <cmath>
#include <span>
#include <vector>
#include <string_view>
#include <iomanip>

namespace radio {

struct ObstaclePoint {
    double distance_from_tx_km;
    double obstacle_height_m;
    std::string_view description;
};

struct TraceReport {
    double distance_km;
    double r1_m;
    double earth_bulge_m;
    double los_height_m;
    double clearance_m;
    double clearance_ratio;
    double diff_loss_db;
    bool is_pass;
};

class FresnelCalculator {
public:
    static constexpr double DefaultKFactor = 1.333333; // 4/3

    explicit FresnelCalculator(double frequency_ghz, double k_factor = DefaultKFactor)
        : frequency_ghz_(frequency_ghz), k_factor_(k_factor) {}

    [[nodiscard]] double calculate_r1(double d1_km, double d2_km, double d_total_km) const noexcept {
        return 17.32 * std::sqrt((d1_km * d2_km) / (frequency_ghz_ * d_total_km));
    }

    [[nodiscard]] double calculate_earth_bulge(double d1_km, double d2_km) const noexcept {
        return (d1_km * d2_km) / (12.74 * k_factor_);
    }

    [[nodiscard]] TraceReport evaluate_obstacle(
        double d_total_km,
        double h_tx_m,
        double h_rx_m,
        const ObstaclePoint& obs
    ) const noexcept {
        const double d1 = obs.distance_from_tx_km;
        const double d2 = d_total_km - d1;

        const double r1 = calculate_r1(d1, d2, d_total_km);
        const double bulge = calculate_earth_bulge(d1, d2);
        const double los = h_tx_m + (h_rx_m - h_tx_m) * (d1 / d_total_km);
        const double clearance = los - (obs.obstacle_height_m + bulge);
        const double ratio = clearance / r1;

        const double loss = compute_diffraction_loss(ratio);

        return TraceReport{
            .distance_km = d1,
            .r1_m = r1,
            .earth_bulge_m = bulge,
            .los_height_m = los,
            .clearance_m = clearance,
            .clearance_ratio = ratio,
            .diff_loss_db = loss,
            .is_pass = (ratio >= 0.6)
        };
    }

    [[nodiscard]] std::vector<TraceReport> evaluate_profile(
        double d_total_km,
        double h_tx_m,
        double h_rx_m,
        std::span<const ObstaclePoint> obstacles
    ) const {
        std::vector<TraceReport> reports;
        reports.reserve(obstacles.size());
        for (const auto& obs : obstacles) {
            reports.push_back(evaluate_obstacle(d_total_km, h_tx_m, h_rx_m, obs));
        }
        return reports;
    }

private:
    double frequency_ghz_;
    double k_factor_;

    static double compute_diffraction_loss(double ratio) noexcept {
        double v = -ratio * 1.41421356;
        if (v < -1.0) return 0.0;
        double v_sub = v - 0.1;
        double arg = std::sqrt(v_sub * v_sub + 1.0) + v_sub;
        if (arg <= 0.0) return 0.0;
        double loss = 6.9 + 20.0 * std::log10(arg);
        return loss < 0.0 ? 0.0 : loss;
    }
};

} // namespace radio

int main() {
    using namespace radio;

    constexpr double total_dist_km = 12.0;
    constexpr double freq_ghz = 5.8;
    constexpr double h_tx = 30.0;
    constexpr double h_rx = 25.0;

    const std::vector<ObstaclePoint> profile = {
        { .distance_from_tx_km = 3.0, .obstacle_height_m = 15.0, .description = "Лісосмуга" },
        { .distance_from_tx_km = 6.0, .obstacle_height_m = 22.0, .description = "Пагорб" },
        { .distance_from_tx_km = 9.0, .obstacle_height_m = 18.0, .description = "Будівля" }
    };

    FresnelCalculator calc(freq_ghz);
    auto reports = calc.evaluate_profile(total_dist_km, h_tx, h_rx, profile);

    std::cout << "=== Профільний аналіз траси (C++20) ===\n";
    std::cout << "Траса: " << total_dist_km << " км, Частота: " << freq_ghz << " ГГц\n\n";

    for (size_t i = 0; i < profile.size(); ++i) {
        const auto& obs = profile[i];
        const auto& rep = reports[i];

        std::cout << "Точка " << (i + 1) << " [" << obs.description << "] на " << obs.distance_from_tx_km << " км:\n"
                  << "  - R1: " << std::fixed << std::setprecision(2) << rep.r1_m << " м\n"
                  << "  - Опуклість Землі: " << rep.earth_bulge_m << " м\n"
                  << "  - Просвіт: " << rep.clearance_m << " м (" << std::setprecision(1) << rep.clearance_ratio * 100.0 << "% від R1)\n"
                  << "  - Втрати: " << std::setprecision(2) << rep.diff_loss_db << " дБ\n"
                  << "  - Критерій 60%: " << (rep.is_pass ? "ПРОЙДЕНО" : "НЕ ПРОЙДЕНО") << "\n\n";
    }

    return 0;
}
