#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <iomanip>

namespace gasdynamics {

enum class ExpansionError {
    SubsonicFlow,        // M1 <= 1.0
    InvalidGamma,        // gamma <= 1.0
    VacuumLimitExceeded  // Turn angle exceeds nu_max
};

struct FlowState {
    double M1;
    double M2;
    double delta_deg;
    double nu1_deg;
    double nu2_deg;
    double mu1_deg;
    double mu2_deg;
    double p_ratio;
    double T_ratio;
    double rho_ratio;
};

class PrandtlMeyerSolver {
public:
    explicit constexpr PrandtlMeyerSolver(double gamma = 1.40) noexcept
        : gamma_{gamma} {}

    [[nodiscard]] double nu(double M) const noexcept {
        if (M <= 1.0) return 0.0;
        const double g_factor = std::sqrt((gamma_ - 1.0) / (gamma_ + 1.0));
        const double term1 = (1.0 / g_factor) * std::atan(g_factor * std::sqrt(M * M - 1.0));
        const double term2 = std::atan(std::sqrt(M * M - 1.0));
        return term1 - term2;
    }

    [[nodiscard]] double mu(double M) const noexcept {
        if (M <= 1.0) return std::numbers::pi / 2.0;
        return std::asin(1.0 / M);
    }

    [[nodiscard]] double nu_max() const noexcept {
        const double g_factor = std::sqrt((gamma_ - 1.0) / (gamma_ + 1.0));
        return (std::numbers::pi / 2.0) * ((1.0 / g_factor) - 1.0);
    }

    [[nodiscard]] double inverse_nu(double nu_target_rad) const noexcept {
        double M = 1.5 + nu_target_rad;
        constexpr double eps = 1e-12;
        constexpr int max_iter = 100;

        for (int i = 0; i < max_iter; ++i) {
            if (M < 1.000001) M = 1.000001;
            const double f = nu(M) - nu_target_rad;
            if (std::abs(f) < eps) break;

            const double df_dM = std::sqrt(M * M - 1.0) / (M * (1.0 + 0.5 * (gamma_ - 1.0) * M * M));
            M -= f / df_dM;
        }
        return M;
    }

    [[nodiscard]] std::expected<FlowState, ExpansionError> solve(double M1, double delta_deg) const noexcept {
        if (M1 <= 1.0) return std::unexpected(ExpansionError::SubsonicFlow);
        if (gamma_ <= 1.0) return std::unexpected(ExpansionError::InvalidGamma);

        const double delta_rad = delta_deg * (std::numbers::pi / 180.0);
        const double nu1_rad = nu(M1);
        const double nu2_rad = nu1_rad + delta_rad;

        if (nu2_rad >= nu_max()) {
            return std::unexpected(ExpansionError::VacuumLimitExceeded);
        }

        const double M2 = inverse_nu(nu2_rad);
        const double tau1 = 1.0 + 0.5 * (gamma_ - 1.0) * M1 * M1;
        const double tau2 = 1.0 + 0.5 * (gamma_ - 1.0) * M2 * M2;
        const double temp_r = tau1 / tau2;

        return FlowState{
            .M1 = M1,
            .M2 = M2,
            .delta_deg = delta_deg,
            .nu1_deg = nu1_rad * (180.0 / std::numbers::pi),
            .nu2_deg = nu2_rad * (180.0 / std::numbers::pi),
            .mu1_deg = mu(M1) * (180.0 / std::numbers::pi),
            .mu2_deg = mu(M2) * (180.0 / std::numbers::pi),
            .p_ratio = std::pow(temp_r, gamma_ / (gamma_ - 1.0)),
            .T_ratio = temp_r,
            .rho_ratio = std::pow(temp_r, 1.0 / (gamma_ - 1.0))
        };
    }

private:
    double gamma_;
};

} // namespace gasdynamics

int main() {
    using namespace gasdynamics;

    PrandtlMeyerSolver solver(1.40);
    const double M1 = 1.50;
    const double delta = 20.0;

    std::cout << "=== Розрахунок течії Прандтля — Майєра (C++23) ===\n";

    auto result = solver.solve(M1, delta);

    if (result.has_value()) {
        const auto& s = result.value();
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "• Вхідні параметри:           M1 = " << s.M1 << ", Δθ = " << s.delta_deg << " deg\n";
        std::cout << "• Вихідне число Маха M2:       " << s.M2 << "\n";
        std::cout << "• Функція ν(M1) -> ν(M2):     " << s.nu1_deg << " deg -> " << s.nu2_deg << " deg\n";
        std::cout << "• Кути Маха μ(M1) -> μ(M2):    " << s.mu1_deg << " deg -> " << s.mu2_deg << " deg\n";
        std::cout << "• Відношення тисків p2/p1:     " << s.p_ratio << "\n";
        std::cout << "• Відношення температур T2/T1: " << s.T_ratio << "\n";
        std::cout << "• Відношення густин ρ2/ρ1:    " << s.rho_ratio << "\n";
    } else {
        switch (result.error()) {
            case ExpansionError::SubsonicFlow:
                std::cerr << "Помилка: Вхідний потік має бути надзвуковим (M1 > 1.0).\n";
                break;
            case ExpansionError::InvalidGamma:
                std::cerr << "Помилка: Показник адіабати gamma має бути більше 1.0.\n";
                break;
            case ExpansionError::VacuumLimitExceeded:
                std::cerr << "Помилка: Перевищено граничний кут розширення в вакуум.\n";
                break;
        }
    }

    return 0;
}
