#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace drone_mechanics {

struct CompositeMaterial {
    double E1{135.0e9};      // Па: поздовжній модуль Юнга
    double E2{9.0e9};        // Па: поперечний модуль Юнга
    double G12{4.8e9};       // Па: модуль зсуву
    double nu12{0.30};       // Коефіцієнт Пуассона
    double Xt{2100.0e6};     // Па: міцність на поздовжній розтяг
    double Xc{1200.0e6};     // Па: міцність на поздовжній стиск
    double Yt{50.0e6};       // Па: міцність на поперечний розтяг
    double Yc{180.0e6};      // Па: міцність на поперечний стиск
    double S{75.0e6};        // Па: міцність на зсув
    double ply_thickness{0.125e-3}; // м: товщина одного шару
};

struct BeamResult {
    double Ex_eff_gpa{0.0};
    double deflection_mm{0.0};
    double min_safety_factor{0.0};
};

class CompositeTubeCalculator {
public:
    explicit CompositeTubeCalculator(CompositeMaterial mat, std::vector<double> layup_deg)
        : mat_(mat), layup_(std::move(layup_deg)) {}

    [[nodiscard]] std::optional<BeamResult> evaluate(
        double length_m,
        double outer_radius_m,
        double thrust_force_n
    ) const {
        if (layup_.empty() || length_m <= 0.0 || outer_radius_m <= 0.0) {
            return std::nullopt;
        }

        const double nu21 = (mat_.nu12 * mat_.E2) / mat_.E1;
        const double denom = 1.0 - mat_.nu12 * nu21;

        const double Q11 = mat_.E1 / denom;
        const double Q12 = (mat_.nu12 * mat_.E2) / denom;
        const double Q22 = mat_.E2 / denom;
        const double Q66 = mat_.G12;

        double A11 = 0.0, A12 = 0.0, A22 = 0.0;
        const double total_thickness = layup_.size() * mat_.ply_thickness;

        for (double angle_deg : layup_) {
            const double rad = angle_deg * (std::numbers::pi / 180.0);
            const double m = std::cos(rad);
            const double n = std::sin(rad);
            const double m2 = m * m, n2 = n * n;
            const double m4 = m2 * m2, n4 = n2 * n2, m2n2 = m2 * n2;

            const double Qbar11 = Q11 * m4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * n4;
            const double Qbar12 = (Q11 + Q22 - 4.0 * Q66) * m2n2 + Q12 * (m4 + n4);
            const double Qbar22 = Q11 * n4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * m4;

            A11 += Qbar11 * mat_.ply_thickness;
            A12 += Qbar12 * mat_.ply_thickness;
            A22 += Qbar22 * mat_.ply_thickness;
        }

        const double Ex_eff = (A11 * A22 - A12 * A12) / (total_thickness * A22);
        const double inner_radius_m = outer_radius_m - total_thickness;
        const double I_xx = (std::numbers::pi / 4.0) * (std::pow(outer_radius_m, 4.0) - std::pow(inner_radius_m, 4.0));

        const double w_max = (thrust_force_n * std::pow(length_m, 3.0)) / (3.0 * Ex_eff * I_xx);
        const double M_bend = thrust_force_n * length_m;
        const double eps_x_max = (M_bend * outer_radius_m) / (Ex_eff * I_xx);

        double min_sf = 1e9;
        for (double angle_deg : layup_) {
            const double rad = angle_deg * (std::numbers::pi / 180.0);
            const double m = std::cos(rad);
            const double n = std::sin(rad);

            const double eps1 = eps_x_max * m * m;
            const double eps2 = eps_x_max * n * n;
            const double gamma12 = -2.0 * eps_x_max * m * n;

            const double sigma1 = Q11 * eps1 + Q12 * eps2;
            const double sigma2 = Q12 * eps1 + Q22 * eps2;
            const double tau12  = Q66 * gamma12;

            const double sf = compute_tsai_wu_sf(sigma1, sigma2, tau12);
            if (sf < min_sf) min_sf = sf;
        }

        return BeamResult{
            .Ex_eff_gpa = Ex_eff / 1e9,
            .deflection_mm = w_max * 1e3,
            .min_safety_factor = min_sf
        };
    }

private:
    [[nodiscard]] double compute_tsai_wu_sf(double s1, double s2, double t12) const noexcept {
        const double F1 = (1.0 / mat_.Xt) - (1.0 / mat_.Xc);
        const double F2 = (1.0 / mat_.Yt) - (1.0 / mat_.Yc);
        const double F11 = 1.0 / (mat_.Xt * mat_.Xc);
        const double F22 = 1.0 / (mat_.Yt * mat_.Yc);
        const double F66 = 1.0 / (mat_.S * mat_.S);
        const double F12 = -0.5 * std::sqrt(F11 * F22);

        const double A = F11 * s1 * s1 + F22 * s2 * s2 + F66 * t12 * t12 + 2.0 * F12 * s1 * s2;
        const double B = F1 * s1 + F2 * s2;

        if (A <= 1e-20) return 100.0;
        const double discr = B * B + 4.0 * A;
        return (discr < 0.0) ? 0.0 : (-B + std::sqrt(discr)) / (2.0 * A);
    }

    CompositeMaterial mat_;
    std::vector<double> layup_;
};

} // namespace drone_mechanics

int main() {
    using namespace drone_mechanics;

    CompositeMaterial carbon_t700{};
    std::vector<double> quasi_layup{0.0, 45.0, -45.0, 90.0, 90.0, -45.0, 45.0, 0.0};

    CompositeTubeCalculator calculator(carbon_t700, quasi_layup);
    if (const auto res = calculator.evaluate(0.35, 0.0125, 45.0)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Ефективний модуль Ex: " << res->Ex_eff_gpa << " ГПа\n";
        std::cout << "Прогин на кінці: " << res->deflection_mm << " мм\n";
        std::cout << "Мінімальний запас міцності: " << res->min_safety_factor << "\n";
    }
    return 0;
}
