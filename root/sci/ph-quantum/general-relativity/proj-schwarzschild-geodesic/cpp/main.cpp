#include <iostream>
#include <vector>
#include <cmath>
#include <utility>
#include <iomanip>

struct GeodesicPoint {
    double phi{0.0};
    double r{0.0};
    double u{0.0};
    double w{0.0};
};

class SchwarzschildSimulator {
public:
    explicit SchwarzschildSimulator(double r_s) noexcept : r_s_(r_s) {}

    [[nodiscard]] std::vector<GeodesicPoint> compute_trajectory(
        double r_initial, double impact_b, double dphi = 0.0005, std::size_t max_steps = 50000) const 
    {
        std::vector<GeodesicPoint> trajectory;
        trajectory.reserve(4096);

        double u = 1.0 / r_initial;
        const double w_sq = 1.0 / (impact_b * impact_b) - u * u * (1.0 - r_s_ * u);
        double w = std::sqrt(std::max(0.0, w_sq));
        double phi = 0.0;

        auto rhs = [this](double u_val, double w_val) noexcept -> std::pair<double, double> {
            return { w_val, 1.5 * r_s_ * u_val * u_val - u_val };
        };

        for (std::size_t step = 0; step < max_steps; ++step) {
            const double r_curr = (u > 1e-15) ? (1.0 / u) : 1e15;
            trajectory.push_back({ phi, r_curr, u, w });

            if (u >= (1.0 / r_s_)) {
                // Фотон затягнуто під горизонт подій
                break;
            }

            if (u <= 0.0 && phi > 1.57079632679) {
                // Виліт на нескінченність
                break;
            }

            const auto [k1_u, k1_w] = rhs(u, w);
            const auto [k2_u, k2_w] = rhs(u + 0.5 * dphi * k1_u, w + 0.5 * dphi * k1_w);
            const auto [k3_u, k3_w] = rhs(u + 0.5 * dphi * k2_u, w + 0.5 * dphi * k2_w);
            const auto [k4_u, k4_w] = rhs(u + dphi * k3_u, w + dphi * k3_w);

            u += (dphi / 6.0) * (k1_u + 2.0 * k2_u + 2.0 * k3_u + k4_u);
            w += (dphi / 6.0) * (k1_w + 2.0 * k2_w + 2.0 * k3_w + k4_w);
            phi += dphi;
        }

        return trajectory;
    }

private:
    double r_s_;
};

int main() {
    constexpr double sun_rs = 2950.0;
    constexpr double sun_radius = 6.96e8;

    const SchwarzschildSimulator sim(sun_rs);
    const auto trajectory = sim.compute_trajectory(1.0e11, sun_radius);

    std::cout << "C++ симуляція закінчена. Обчислено точок: " << trajectory.size() << "\n";
    if (!trajectory.empty()) {
        const double final_phi = trajectory.back().phi;
        const double defl_arcsec = std::abs(final_phi - M_PI) * (180.0 / M_PI) * 3600.0;
        std::cout << std::fixed << std::setprecision(3)
                  << "Розраховане гравітаційне відхилення світла: " << defl_arcsec << " кутових секунд.\n";
    }

    return 0;
}
