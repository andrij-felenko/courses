// Modern C++20 Implementation of PP-Chain Branching and Energy Solver
#include <iostream>
#include <cmath>
#include <array>
#include <span>
#include <string_view>
#include <expected>
#include <iomanip>

namespace astro::physics {

struct CoreConditions {
    double temp_k{15.7e6};
    double density_gcm3{150.0};
    double x_hyd{0.35};
    double y_hel{0.63};

    [[nodiscard]] constexpr double t6() const noexcept {
        return temp_k / 1.0e6;
    }
};

struct ChainBranching {
    double pp1{0.0};
    double pp2{0.0};
    double pp3{0.0};
    double hep{0.0};
    double q_eff_mev{0.0};
    double nu_loss_mev{0.0};
    double energy_gen_wkg{0.0};

    void print_summary(std::string_view label) const {
        std::cout << "=== " << label << " ===\n"
                  << std::fixed << std::setprecision(4)
                  << "Частка pp-I:   " << pp1 * 100.0 << " %\n"
                  << "Частка pp-II:  " << pp2 * 100.0 << " %\n"
                  << "Частка pp-III: " << pp3 * 100.0 << " %\n"
                  << "Нейтринні втрати: " << nu_loss_mev << " МЕв\n"
                  << "Корисне Q_eff:    " << q_eff_mev << " МЕв\n"
                  << "Енерговиділення:  " << std::scientific << energy_gen_wkg << " Вт/кг\n";
    }
};

enum class SolverError {
    InvalidTemperature,
    InvalidDensity,
    InvalidComposition
};

class PPChainSolver {
public:
    [[nodiscard]] static std::expected<ChainBranching, SolverError> 
    compute(const CoreConditions& cond) noexcept {
        if (cond.temp_k <= 0.0) return std::unexpected(SolverError::InvalidTemperature);
        if (cond.density_gcm3 <= 0.0) return std::unexpected(SolverError::InvalidDensity);
        if (cond.x_hyd < 0.0 || cond.x_hyd > 1.0) return std::unexpected(SolverError::InvalidComposition);

        ChainBranching res{};
        const double t6 = cond.t6();
        const double rho = cond.density_gcm3;
        const double X = cond.x_hyd;
        const double Y = cond.y_hel;

        const double t6_13 = std::cbrt(t6);
        const double t6_23 = t6_13 * t6_13;

        // Швидкісні коефіцієнти взаємодії
        const double r11 = 4.0e-15 * (1.0 / t6_23) * std::exp(-33.804 / t6_13);
        const double r33 = 1.2e+04 * (1.0 / t6_23) * std::exp(-122.76 / t6_13);
        const double r34 = 5.6e+05 * (1.0 / t6_23) * std::exp(-128.01 / t6_13);
        const double r71 = 3.1e+05 * (1.0 / t6_23) * std::exp(-137.56 / t6_13);

        const double mu_e = 2.0 / (1.0 + X);
        const double lambda_7e = 1.34e-9 * (rho / mu_e) * (1.0 / std::sqrt(t6));

        const double ratio_34_33 = (r34 * Y) / (r33 * X + 1.0e-30);
        const double f_be = ratio_34_33 / (1.0 + ratio_34_33);

        res.pp1 = 1.0 - f_be;
        const double ratio_71_7e = (r71 * X * rho) / (lambda_7e + 1.0e-30);
        res.pp3 = f_be * (ratio_71_7e / (1.0 + ratio_71_7e));
        res.pp2 = f_be - res.pp3;
        res.hep = 2.0e-7;

        res.nu_loss_mev = res.pp1 * 0.530 + res.pp2 * 1.127 + res.pp3 * 6.975;
        res.q_eff_mev = 26.731 - res.nu_loss_mev;

        const double eps = 0.241 * rho * X * X * (1.0 / t6_23) * std::exp(-33.804 / t6_13);
        res.energy_gen_wkg = eps * 1.0e-4;

        return res;
    }
};

} // namespace astro::physics

int main() {
    using namespace astro::physics;

    constexpr CoreConditions sun_core{.temp_k = 15.7e6, .density_gcm3 = 150.0, .x_hyd = 0.35, .y_hel = 0.63};

    if (auto result = PPChainSolver::compute(sun_core); result.has_value()) {
        result->print_summary("РЕЗУЛЬТАТ СИМУЛЯЦІЇ PP-ЛАНЦЮЖКА (C++20)");
    } else {
        std::cerr << "Помилка обчислення параметрів ядра!\n";
    }

    return 0;
}
