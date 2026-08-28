#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <span>
#include <iomanip>

struct AntennaDirectivity {
    double directivity_linear{0.0};
    double directivity_dbi{0.0};
    double p_rad_watts{0.0};
    double u_max{0.0};
    double hpbw_theta_deg{0.0};
    double hpbw_phi_deg{0.0};
};

class DirectivityCalculator {
public:
    static AntennaDirectivity compute(
        std::span<const double> grid,
        size_t theta_steps,
        size_t phi_steps,
        double dynamic_range_db = 40.0)
    {
        if (grid.size() < (theta_steps + 1) * (phi_steps + 1) || theta_steps < 2 || phi_steps < 2) {
            return {};
        }

        const double d_theta = std::numbers::pi / static_cast<double>(theta_steps);
        const double d_phi = (2.0 * std::numbers::pi) / static_cast<double>(phi_steps);

        // Крок 1: Знаходимо U_max
        double u_max = 0.0;
        for (const double u_val : grid) {
            u_max = std::max(u_max, u_val);
        }

        const double noise_floor = u_max * std::pow(10.0, -dynamic_range_db / 10.0);

        // Крок 2: Інтегрування трапеціями
        double p_rad = 0.0;
        for (size_t i = 0; i <= theta_steps; ++i) {
            const double theta = static_cast<double>(i) * d_theta;
            const double sin_theta = std::sin(theta);
            const double w_theta = (i == 0 || i == theta_steps) ? 0.5 : 1.0;

            for (size_t j = 0; j < phi_steps; ++j) {
                const size_t idx = i * (phi_steps + 1) + j;
                double u_val = grid[idx];

                if (u_val < noise_floor) {
                    u_val = 0.0;
                }

                p_rad += u_val * sin_theta * w_theta;
            }
        }

        p_rad *= (d_theta * d_phi);

        AntennaDirectivity result{};
        if (p_rad > 1e-15 && u_max > 0.0) {
            result.u_max = u_max;
            result.p_rad_watts = p_rad;
            result.directivity_linear = (4.0 * std::numbers::pi * u_max) / p_rad;
            result.directivity_dbi = 10.0 * std::log10(result.directivity_linear);
        }

        return result;
    }
};

int main() {
    constexpr size_t theta_steps = 180;
    constexpr size_t phi_steps = 360;
    const size_t total_points = (theta_steps + 1) * (phi_steps + 1);

    std::vector<double> grid(total_points);

    // Тест для ізотропного випромінювача U(θ, ϕ) = 1.0
    std::fill(grid.begin(), grid.end(), 1.0);

    auto res = DirectivityCalculator::compute(grid, theta_steps, phi_steps);

    std::cout << "--- Тест ізотропного випромінювача (C++) ---\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "U_max    = " << res.u_max << " Вт/ст\n";
    std::cout << "P_rad    = " << res.p_rad_watts << " Вт (очікується 4π ≈ 12.5664)\n";
    std::cout << "D_linear = " << res.directivity_linear << " (очікується 1.0000)\n";
    std::cout << "D_dBi    = " << res.directivity_dbi << " dBi (очікується 0.00 dBi)\n";

    return 0;
}
