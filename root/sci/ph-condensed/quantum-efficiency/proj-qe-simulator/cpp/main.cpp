#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>
#include <expected>
#include <algorithm>

namespace physics {

constexpr double hc_ev_nm = 1239.8419;
constexpr double silicon_eg_ev = 1.12;

struct SpectrumPoint {
    double wavelength_nm{};
    double reflection_r{};
    double alpha_cm1{};
    double iqe{};
    double eqe{};
    double responsivity_a_w{};
};

enum class SimulationError {
    invalid_parameters,
    out_of_bounds
};

class PhotodiodeSimulator {
public:
    explicit PhotodiodeSimulator(double depletion_width_um,
                                 double diffusion_length_um,
                                 double ar_coating_lambda_nm)
        : w_cm_(depletion_width_um * 1e-4),
          ln_cm_(diffusion_length_um * 1e-4),
          ar_target_nm_(ar_coating_lambda_nm) {}

    [[nodiscard]] std::expected<std::vector<SpectrumPoint>, SimulationError>
    generate_spectrum(double start_nm, double end_nm, std::size_t num_points) const {
        if (start_nm >= end_nm || num_points == 0) {
            return std::unexpected(SimulationError::invalid_parameters);
        }

        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(num_points);

        const double step = (end_nm - start_nm) / static_cast<double>(num_points - 1);

        for (std::size_t i = 0; i < num_points; ++i) {
            const double lambda = start_nm + static_cast<double>(i) * step;
            const double r = calculate_reflection(lambda);
            const double alpha = calculate_alpha(lambda);

            double iqe = 0.0;
            if (alpha > 0.0) {
                const double exp_aw = std::exp(-alpha * w_cm_);
                iqe = std::clamp(1.0 - (exp_aw / (1.0 + alpha * ln_cm_)), 0.0, 1.0);
            }

            const double eqe = (1.0 - r) * iqe;
            const double responsivity = (eqe * (lambda * 1e-3)) / 1.23984;

            spectrum.push_back(SpectrumPoint{
                .wavelength_nm = lambda,
                .reflection_r = r,
                .alpha_cm1 = alpha,
                .iqe = iqe,
                .eqe = eqe,
                .responsivity_a_w = responsivity
            });
        }

        return spectrum;
    }

private:
    double w_cm_;
    double ln_cm_;
    double ar_target_nm_;

    [[nodiscard]] static double calculate_alpha(double lambda_nm) noexcept {
        if (lambda_nm >= 1107.0) return 0.0;
        const double photon_energy = hc_ev_nm / lambda_nm;
        const double diff = photon_energy - silicon_eg_ev;
        if (diff <= 0.0) return 0.0;
        return 5000.0 * diff * diff + 1e5 * std::pow(diff, 3.5);
    }

    [[nodiscard]] double calculate_reflection(double lambda_nm) const noexcept {
        constexpr double n_si = 3.8;
        constexpr double r_bare = ((n_si - 1.0) / (n_si + 1.0)) * ((n_si - 1.0) / (n_si + 1.0));
        const double dev = (lambda_nm - ar_target_nm_) / ar_target_nm_;
        const double r_ar = r_bare * (dev * dev + 0.05);
        return std::min(r_bare, r_ar);
    }
};

} // namespace physics

int main() {
    using namespace physics;

    const PhotodiodeSimulator sim(20.0, 50.0, 633.0);
    const auto result = sim.generate_spectrum(300.0, 1150.0, 10);

    if (!result) {
        std::cerr << "Помилка симуляції фотодіода.\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "λ (нм) | R (%)  | α (см⁻¹) | IQE (%) | EQE (%) | R_λ (А/Вт)\n";
    std::cout << "-------+--------+----------+---------+---------+-----------\n";

    for (const auto& pt : *result) {
        std::cout << std::setw(6) << pt.wavelength_nm << " | "
                  << std::setw(6) << pt.reflection_r * 100.0 << " | "
                  << std::setw(8) << std::setprecision(1) << pt.alpha_cm1 << " | "
                  << std::setw(7) << std::setprecision(2) << pt.iqe * 100.0 << " | "
                  << std::setw(7) << pt.eqe * 100.0 << " | "
                  << std::setw(9) << std::setprecision(4) << pt.responsivity_a_w << "\n";
    }

    return 0;
}
