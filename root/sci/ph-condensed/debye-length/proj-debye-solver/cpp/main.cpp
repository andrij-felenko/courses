#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <numbers>

namespace physics {

struct DebyeParams {
    double temp_k{300.0};       // Температура в Кельвінах
    double rel_perm{11.7};      // Відносна проникність (кремній = 11.7)
    double n0_m3{1.0e22};       // Концентрація носіїв м⁻³

    [[nodiscard]] constexpr double debye_length() const noexcept {
        constexpr double kb_ev = 8.617333262e-5;
        constexpr double eps0 = 8.854187812e-12;
        constexpr double q = 1.602176634e-19;
        
        const double eps = rel_perm * eps0;
        const double vt = kb_ev * temp_k;
        return std::sqrt((eps * vt) / (2.0 * n0_m3 * q));
    }
};

struct SimulationPoint {
    double x_m;
    double potential_v;
    double charge_density_c_m3;
};

enum class SimulationError {
    InvalidParameters,
    ConvergenceFailed
};

class DebyeSolver {
public:
    [[nodiscard]] static std::expected<std::vector<SimulationPoint>, SimulationError>
    solve_planar(const DebyeParams& params, double phi0_v, double x_max_m, 
                 std::size_t num_nodes = 500, double tol = 1.0e-7) {
        
        if (num_nodes < 3 || x_max_m <= 0.0) {
            return std::unexpected(SimulationError::InvalidParameters);
        }

        const double ld = params.debye_length();
        const double h = x_max_m / static_cast<double>(num_nodes - 1);
        constexpr double kb_ev = 8.617333262e-5;
        const double vt = kb_ev * params.temp_k;
        const double inv_ld2 = 1.0 / (ld * ld);

        std::vector<double> phi(num_nodes);
        for (std::size_t i = 0; i < num_nodes; ++i) {
            const double x = static_cast<double>(i) * h;
            phi[i] = phi0_v * std::exp(-x / ld);
        }
        phi.front() = phi0_v;
        phi.back() = 0.0;

        constexpr std::size_t max_iter = 20000;
        constexpr double omega = 0.4;
        bool converged = false;

        for (std::size_t iter = 0; iter < max_iter; ++iter) {
            double max_diff = 0.0;
            for (std::size_t i = 1; i < num_nodes - 1; ++i) {
                const double rhs = inv_ld2 * vt * std::sinh(phi[i] / vt);
                const double phi_new = 0.5 * (phi[i + 1] + phi[i - 1] - h * h * rhs);
                const double phi_relaxed = (1.0 - omega) * phi[i] + omega * phi_new;

                max_diff = std::max(max_diff, std::abs(phi_relaxed - phi[i]));
                phi[i] = phi_relaxed;
            }

            if (max_diff < tol) {
                converged = true;
                break;
            }
        }

        if (!converged) {
            return std::unexpected(SimulationError::ConvergenceFailed);
        }

        std::vector<SimulationPoint> result;
        result.reserve(num_nodes);

        constexpr double q = 1.602176634e-19;
        for (std::size_t i = 0; i < num_nodes; ++i) {
            const double x = static_cast<double>(i) * h;
            const double rho = -2.0 * q * params.n0_m3 * std::sinh(phi[i] / vt);
            result.push_back({.x_m = x, .potential_v = phi[i], .charge_density_c_m3 = rho});
        }

        return result;
    }
};

} // namespace physics
