#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace composite {

/* Фізичні константи ортотропного моношару */
struct PlyMaterial {
    double E1{135.0e9};      // Па: поздовжній модуль вздовж волокна
    double E2{9.0e9};        // Па: поперечний модуль
    double G12{4.8e9};       // Па: модуль зсуву в площині
    double nu12{0.30};       // Коефіцієнт Пуассона
    double Xt{2100.0e6};     // Па: міцність на розтяг вздовж волокна
    double Xc{1200.0e6};     // Па: міцність на стиск вздовж волокна
    double Yt{50.0e6};       // Па: міцність на поперечний розтяг
    double Yc{180.0e6};      // Па: міцність на поперечний стиск
    double S{75.0e6};        // Па: міцність на зсув у площині
    double thickness{0.125e-3}; // м: товщина моношару
};

/* Геометрія циліндричного променя */
struct TubeGeometry {
    double length{0.35};       // м: довжина консолі
    double outer_radius{0.0125};// м: зовнішній радіус
    double inner_radius{0.0115};// м: внутрішній радіус

    [[nodiscard]] double moment_of_inertia() const noexcept {
        return (std::numbers::pi / 4.0) * (std::pow(outer_radius, 4.0) - std::pow(inner_radius, 4.0));
    }
};

/* Результати розрахунку характеристик ламінату та балки */
struct AnalysisResult {
    double total_thickness{0.0};
    double Ex_eff{0.0};
    double Gxy_eff{0.0};
    double max_deflection{0.0};
    double min_safety_factor{0.0};
    std::size_t critical_layer{0};
};

using Matrix3x3 = std::array<std::array<double, 3>, 3>;

class LaminateBeamSolver {
public:
    explicit LaminateBeamSolver(PlyMaterial material, std::vector<double> ply_angles_deg)
        : mat_(material), angles_(std::move(ply_angles_deg)) {}

    [[nodiscard]] std::optional<AnalysisResult> solve(const TubeGeometry& geom, double thrust_n) const {
        if (angles_.empty() || geom.length <= 0.0 || geom.outer_radius <= geom.inner_radius) {
            return std::nullopt;
        }

        const auto Q = compute_ply_Q();
        Matrix3x3 A{};
        const double total_h = angles_.size() * mat_.thickness;

        for (double angle_deg : angles_) {
            const auto Qbar = transform_Q(Q, angle_deg);
            for (std::size_t i = 0; i < 3; ++i) {
                for (std::size_t j = 0; j < 3; ++j) {
                    A[i][j] += Qbar[i][j] * mat_.thickness;
                }
            }
        }

        const double Ex_eff = (A[0][0] * A[1][1] - A[0][1] * A[0][1]) / (total_h * A[1][1]);
        const double Gxy_eff = A[2][2] / total_h;
        const double I_xx = geom.moment_of_inertia();

        // Прогин консолі w = F * L^3 / (3 * E * I)
        const double w_max = (thrust_n * std::pow(geom.length, 3.0)) / (3.0 * Ex_eff * I_xx);
        const double M_bend = thrust_n * geom.length;
        const double eps_x_max = (M_bend * geom.outer_radius) / (Ex_eff * I_xx);

        double min_sf = 1e9;
        std::size_t crit_idx = 0;

        for (std::size_t k = 0; k < angles_.size(); ++k) {
            const double rad = angles_[k] * (std::numbers::pi / 180.0);
            const double m = std::cos(rad);
            const double n = std::sin(rad);

            const double eps1 = eps_x_max * m * m;
            const double eps2 = eps_x_max * n * n;
            const double gamma12 = -2.0 * eps_x_max * m * n;

            const double sigma1 = Q[0][0] * eps1 + Q[0][1] * eps2;
            const double sigma2 = Q[1][0] * eps1 + Q[1][1] * eps2;
            const double tau12  = Q[2][2] * gamma12;

            const double sf = compute_tsai_wu_sf(sigma1, sigma2, tau12);
            if (sf < min_sf) {
                min_sf = sf;
                crit_idx = k;
            }
        }

        return AnalysisResult{
            .total_thickness = total_h,
            .Ex_eff = Ex_eff,
            .Gxy_eff = Gxy_eff,
            .max_deflection = w_max,
            .min_safety_factor = min_sf,
            .critical_layer = crit_idx
        };
    }

private:
    [[nodiscard]] Matrix3x3 compute_ply_Q() const noexcept {
        const double nu21 = (mat_.nu12 * mat_.E2) / mat_.E1;
        const double denom = 1.0 - mat_.nu12 * nu21;

        Matrix3x3 Q{};
        Q[0][0] = mat_.E1 / denom;
        Q[0][1] = (mat_.nu12 * mat_.E2) / denom;
        Q[1][0] = Q[0][1];
        Q[1][1] = mat_.E2 / denom;
        Q[2][2] = mat_.G12;
        return Q;
    }

    [[nodiscard]] static Matrix3x3 transform_Q(const Matrix3x3& Q, double angle_deg) noexcept {
        const double rad = angle_deg * (std::numbers::pi / 180.0);
        const double m = std::cos(rad);
        const double n = std::sin(rad);
        const double m2 = m * m;
        const double n2 = n * n;
        const double m4 = m2 * m2;
        const double n4 = n2 * n2;
        const double m2n2 = m2 * n2;

        const double Q11 = Q[0][0], Q12 = Q[0][1], Q22 = Q[1][1], Q66 = Q[2][2];
        Matrix3x3 Qbar{};

        Qbar[0][0] = Q11 * m4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * n4;
        Qbar[1][1] = Q11 * n4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * m4;
        Qbar[0][1] = (Q11 + Q22 - 4.0 * Q66) * m2n2 + Q12 * (m4 + n4);
        Qbar[1][0] = Qbar[0][1];
        Qbar[2][2] = (Q11 + Q22 - 2.0 * Q12 - 2.0 * Q66) * m2n2 + Q66 * (m4 + n4);
        Qbar[0][2] = (Q11 - Q12 - 2.0 * Q66) * m * m2 * n + (Q12 - Q22 + 2.0 * Q66) * m * n * n2;
        Qbar[2][0] = Qbar[0][2];
        Qbar[1][2] = (Q11 - Q12 - 2.0 * Q66) * m * n * n2 + (Q12 - Q22 + 2.0 * Q66) * m * m2 * n;
        Qbar[2][1] = Qbar[1][2];

        return Qbar;
    }

    [[nodiscard]] double compute_tsai_wu_sf(double s1, double s2, double t12) const noexcept {
        const double F1 = (1.0 / mat_.Xt) - (1.0 / mat_.Xc);
        const double F2 = (1.0 / mat_.Yt) - (1.0 / mat_.Yc);
        const double F11 = 1.0 / (mat_.Xt * mat_.Xc);
        const double F22 = 1.0 / (mat_.Yt * mat_.Yc);
        const double F66 = 1.0 / (mat_.S * mat_.S);
        const double F12 = -0.5 * std::sqrt(F11 * F22);

        const double A_coef = F11 * s1 * s1 + F22 * s2 * s2 + F66 * t12 * t12 + 2.0 * F12 * s1 * s2;
        const double B_coef = F1 * s1 + F2 * s2;

        if (A_coef <= 1e-20) {
            return (B_coef <= 1e-20) ? 999.0 : 1.0 / B_coef;
        }

        const double discr = B_coef * B_coef + 4.0 * A_coef;
        return (discr < 0.0) ? 0.0 : (-B_coef + std::sqrt(discr)) / (2.0 * A_coef);
    }

    PlyMaterial mat_;
    std::vector<double> angles_;
};

} // namespace composite

int main() {
    using namespace composite;

    PlyMaterial carbon_t700{};
    std::vector<double> quasi_isotropic_layup{0.0, 45.0, -45.0, 90.0, 90.0, -45.0, 45.0, 0.0};
    TubeGeometry quad_arm{.length = 0.35, .outer_radius = 0.0125, .inner_radius = 0.0115};

    LaminateBeamSolver solver(carbon_t700, quasi_isotropic_layup);
    const double motor_thrust = 45.0; // 45 Н

    if (const auto res = solver.solve(quad_arm, motor_thrust)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- C++ CLT Результати аналізу променя ---\n";
        std::cout << "Товщина стінки: " << res->total_thickness * 1e3 << " мм\n";
        std::cout << "Ефективний модуль Ex: " << res->Ex_eff / 1e9 << " ГПа\n";
        std::cout << "Ефективний модуль Gxy: " << res->Gxy_eff / 1e9 << " ГПа\n";
        std::cout << "Максимальний прогин: " << res->max_deflection * 1e3 << " мм\n";
        std::cout << "Коефіцієнт запасу Цая-Ву: " << res->min_safety_factor
                  << " (критичний шар #" << res->critical_layer + 1 << ")\n";
    }

    return 0;
}
