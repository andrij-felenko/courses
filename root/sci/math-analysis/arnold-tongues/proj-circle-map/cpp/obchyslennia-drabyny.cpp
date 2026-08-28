#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

namespace physics::numerical {

struct StaircasePoint {
    double omega{0.0};
    double rotation_number{0.0};
    double derivative{0.0};
};

class DevilsStaircaseCalculator {
public:
    DevilsStaircaseCalculator(double k, std::size_t points_count, std::size_t steps)
        : k_{k}, points_count_{points_count}, steps_{steps} {}

    [[nodiscard]] std::vector<StaircasePoint> calculate() const {
        std::vector<StaircasePoint> points(points_count_);
        const double two_pi = 2.0 * std::numbers::pi;
        const double d_omega = 1.0 / static_cast<double>(points_count_ - 1);

        for (std::size_t i = 0; i < points_count_; ++i) {
            const double omega = static_cast<double>(i) * d_omega;
            double x = 0.1;

            // Перехідний процес
            for (std::size_t s = 0; s < steps_; ++s) {
                x = x + omega - (k_ / two_pi) * std::sin(two_pi * x);
            }

            // Вимірювання
            const double start_x = x;
            for (std::size_t s = 0; s < steps_; ++s) {
                x = x + omega - (k_ / two_pi) * std::sin(two_pi * x);
            }

            const double w = (x - start_x) / static_cast<double>(steps_);
            points[i] = StaircasePoint{.omega = omega, .rotation_number = w, .derivative = 0.0};
        }

        // Центральні різниці для похідної
        for (std::size_t i = 1; i < points_count_ - 1; ++i) {
            points[i].derivative = (points[i + 1].rotation_number - points[i - 1].rotation_number) / (2.0 * d_omega);
        }

        return points;
    }

private:
    double k_;
    std::size_t points_count_;
    std::size_t steps_;
};

} // namespace physics::numerical

int main() {
    using namespace physics::numerical;

    const DevilsStaircaseCalculator calc{1.0, 11, 5000};
    const auto points = calc.calculate();

    std::cout << "=== Таблиця драбини диявола (K = 1.0) ===\n";
    std::cout << "   Omega  |  W(Omega) |   dW/dOmega\n";
    std::cout << "-----------------------------------\n";
    std::cout << std::fixed << std::setprecision(4);

    for (const auto& pt : points) {
        std::cout << "  " << pt.omega << "  |  " << std::setprecision(6) << pt.rotation_number
                  << " |  " << std::setprecision(4) << pt.derivative << "\n";
    }

    return 0;
}
