/* cpp */
#include <iostream>
#include <cmath>
#include <vector>
#include <string_view>
#include <iomanip>
#include <expected>
#include <numbers>

namespace physics {

constexpr double kBoltzmannEv = 8.617333262145e-5; // еВ/К

struct SemiconductorSpecs {
    double bandgap_ev{1.12};       // E_g при 300 K (Si)
    double nc_300{2.86e19};        // N_c при 300 K, см^-3
    double nv_300{3.10e19};        // N_v при 300 K, см^-3
    double donor_conc{1.0e16};     // N_d, см^-3
    double donor_bind_ev{0.045};   // E_c - E_d (Фосфор)
    double acceptor_conc{0.0};     // N_a, см^-3
    double acceptor_bind_ev{0.045};// E_a - E_v
};

struct SimulationPoint {
    double temperature_k;
    double fermi_level_ev;
    double electron_conc;
    double hole_conc;
    double intrinsic_conc;
    std::string_view regime;
};

enum class SolverError {
    InvalidTemperature,
    ConvergenceFailed
};

class FermiSolver {
public:
    explicit FermiSolver(SemiconductorSpecs specs) : specs_(specs) {}

    [[nodiscard]] std::expected<SimulationPoint, SolverError>
    calculate_point(double temp_k) const {
        if (temp_k <= 0.0) {
            return std::unexpected(SolverError::InvalidTemperature);
        }

        double low = 0.0;
        double high = specs_.bandgap_ev;
        double mid = 0.5 * (low + high);

        for (int iter = 0; iter < 120; ++iter) {
            mid = 0.5 * (low + high);
            double imbalance = charge_imbalance(mid, temp_k);

            if (std::abs(imbalance) < 1.0e-6 || (high - low) < 1.0e-8) {
                double kbt = kBoltzmannEv * temp_k;
                double nc = specs_.nc_300 * std::pow(temp_k / 300.0, 1.5);
                double nv = specs_.nv_300 * std::pow(temp_k / 300.0, 1.5);

                double n = nc * std::exp(-(specs_.bandgap_ev - mid) / kbt);
                double p = nv * std::exp(-mid / kbt);
                double ni = std::sqrt(nc * nv) * std::exp(-specs_.bandgap_ev / (2.0 * kbt));

                std::string_view regime = "Домішковий";
                if (temp_k < 100.0) {
                    regime = "Виморожування";
                } else if (n < 1.05 * ni) {
                    regime = "Власний";
                }

                return SimulationPoint{temp_k, mid, n, p, ni, regime};
            }

            if (imbalance > 0.0) {
                low = mid;
            } else {
                high = mid;
            }
        }

        return std::unexpected(SolverError::ConvergenceFailed);
    }

private:
    SemiconductorSpecs specs_;

    [[nodiscard]] double charge_imbalance(double ef, double temp_k) const {
        double kbt = kBoltzmannEv * temp_k;
        double nc = specs_.nc_300 * std::pow(temp_k / 300.0, 1.5);
        double nv = specs_.nv_300 * std::pow(temp_k / 300.0, 1.5);

        double n = nc * std::exp(-(specs_.bandgap_ev - ef) / kbt);
        double p = nv * std::exp(-ef / kbt);

        double nd_plus = specs_.donor_conc / (1.0 + 2.0 * std::exp((ef - (specs_.bandgap_ev - specs_.donor_bind_ev)) / kbt));
        double na_minus = specs_.acceptor_conc / (1.0 + 4.0 * std::exp((specs_.acceptor_bind_ev - ef) / kbt));

        return p + nd_plus - n - na_minus;
    }
};

} // namespace physics

int main() {
    using namespace physics;

    FermiSolver solver{SemiconductorSpecs{
        .bandgap_ev = 1.12,
        .nc_300 = 2.86e19,
        .nv_300 = 3.10e19,
        .donor_conc = 1.0e16,
        .donor_bind_ev = 0.045
    }};

    std::cout << std::string(72, '=') << '\n';
    std::cout << "T (K)  | E_F (еВ) | n (см^-3)    | p (см^-3)    | n_i (см^-3)  | Режим\n";
    std::cout << std::string(72, '=') << '\n';

    for (double t = 50.0; t <= 600.0; t += 50.0) {
        auto result = solver.calculate_point(t);
        if (result) {
            const auto& pt = *result;
            std::cout << std::setw(6) << std::fixed << std::setprecision(1) << pt.temperature_k << " | "
                      << std::setw(8) << std::setprecision(4) << pt.fermi_level_ev << " | "
                      << std::setw(12) << std::scientific << std::setprecision(4) << pt.electron_conc << " | "
                      << std::setw(12) << pt.hole_conc << " | "
                      << std::setw(12) << pt.intrinsic_conc << " | "
                      << pt.regime << '\n';
        }
    }
    std::cout << std::string(72, '=') << '\n';

    return 0;
}
