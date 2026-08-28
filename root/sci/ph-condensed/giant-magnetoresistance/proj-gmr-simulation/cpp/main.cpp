#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

class GmrSpinValveSim {
public:
    struct DataPoint {
        double h_field;
        double theta_free;
        double resistance;
        bool is_sweep_up;
    };

    explicit constexpr GmrSpinValveSim(double r_p = 100.0, double gmr_ratio = 0.12, 
                                       double h_c = 0.5, double h_ex = 25.0) noexcept
        : r_p_{r_p}, r_ap_{r_p * (1.0 + gmr_ratio)}, h_c_{h_c}, h_ex_{h_ex} {}

    [[nodiscard]] double calculate_free_angle(double h_field, bool sweep_up) const noexcept {
        if (sweep_up) {
            if (h_field < -h_c_) return std::numbers::pi;
            if (h_field > h_c_) return 0.0;
            return std::numbers::pi;
        } else {
            if (h_field > h_c_) return 0.0;
            if (h_field < -h_c_) return std::numbers::pi;
            return 0.0;
        }
    }

    [[nodiscard]] double calculate_pinned_angle(double h_field) const noexcept {
        return (h_field > -h_ex_) ? 0.0 : std::numbers::pi;
    }

    [[nodiscard]] double compute_resistance(double theta_free, double theta_pinned) const noexcept {
        const double cos_angle = std::cos(theta_free - theta_pinned);
        return r_p_ + 0.5 * (r_ap_ - r_p_) * (1.0 - cos_angle);
    }

    [[nodiscard]] std::vector<DataPoint> run_sweep(double h_min, double h_max, std::size_t steps) const {
        std::vector<DataPoint> results;
        results.reserve((steps + 1) * 2);
        const double step_size = (h_max - h_min) / static_cast<double>(steps);

        for (std::size_t i = 0; i <= steps; ++i) {
            const double h = h_min + static_cast<double>(i) * step_size;
            const double tf = calculate_free_angle(h, true);
            const double tp = calculate_pinned_angle(h);
            results.push_back({h, tf, compute_resistance(tf, tp), true});
        }

        for (std::size_t i = 0; i <= steps; ++i) {
            const double h = h_max - static_cast<double>(i) * step_size;
            const double tf = calculate_free_angle(h, false);
            const double tp = calculate_pinned_angle(h);
            results.push_back({h, tf, compute_resistance(tf, tp), false});
        }

        return results;
    }

private:
    double r_p_;
    double r_ap_;
    double h_c_;
    double h_ex_;
};

int main() {
    const GmrSpinValveSim sim{100.0, 0.10, 0.8, 20.0};
    const auto data = sim.run_sweep(-30.0, 30.0, 10);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << " H (mT) | theta_free (rad) | R (Ohm)\n";
    std::cout << "------------------------------------\n";
    for (std::size_t i = 0; i < 6 && i < data.size(); ++i) {
        std::cout << std::setw(7) << data[i].h_field << " | "
                  << std::setw(16) << data[i].theta_free << " | "
                  << std::setw(7) << data[i].resistance << "\n";
    }
    return 0;
}
