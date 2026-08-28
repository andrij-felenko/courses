#include <iostream>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string>
#include <algorithm>

namespace physics {

constexpr double kBoltzEv = 8.617333262145e-5; // еВ/К

struct SemiconductorConfig {
    double temp_k{300.0};
    double n_d{1.0e16};          // см⁻³
    double e_d_relative{0.045};  // еВ відносно Ec
    double n_a{0.0};             // см⁻³
    double e_a_relative{0.045};  // еВ відносно Ev
    double m_e_eff{1.08};
    double m_h_eff{0.81};
};

struct CalculationResult {
    double e_v_ev;
    double e_c_ev;
    double e_g_ev;
    double e_f_ev;
    double n_elec_cm3;
    double p_hole_cm3;
    double n_d_plus_cm3;
    double n_a_minus_cm3;
};

enum class SolverErrorCode {
    InvalidTemperature,
    InvalidDoping
};

class FermiLevelSolver {
public:
    [[nodiscard]] static double calculate_varshni_bandgap(double temp_k) noexcept {
        constexpr double eg0 = 1.166;
        constexpr double alpha = 4.73e-4;
        constexpr double beta = 636.0;
        return eg0 - (alpha * temp_k * temp_k) / (temp_k + beta);
    }

    [[nodiscard]] static std::expected<CalculationResult, SolverErrorCode> solve(
        const SemiconductorConfig& cfg, double tolerance_ev = 1.0e-8) noexcept
    {
        if (cfg.temp_k <= 0.0) {
            return std::unexpected(SolverErrorCode::InvalidTemperature);
        }
        if (cfg.n_d < 0.0 || cfg.n_a < 0.0) {
            return std::unexpected(SolverErrorCode::InvalidDoping);
        }

        const double e_v = 0.0;
        const double e_g = calculate_varshni_bandgap(cfg.temp_k);
        const double e_c = e_v + e_g;
        const double e_d = e_c - cfg.e_d_relative;
        const double e_a = e_v + cfg.e_a_relative;

        const double t_factor = cfg.temp_k / 300.0;
        const double nc = 2.86e19 * std::pow(cfg.m_e_eff / 1.08, 1.5) * std::pow(t_factor, 1.5);
        const double nv = 3.10e19 * std::pow(cfg.m_h_eff / 0.81, 1.5) * std::pow(t_factor, 1.5);
        const double kt = kBoltzEv * cfg.temp_k;

        auto residual = [&](double e_f) noexcept -> double {
            const double arg_n = std::clamp(-(e_c - e_f) / kt, -80.0, 80.0);
            const double arg_p = std::clamp(-(e_f - e_v) / kt, -80.0, 80.0);

            const double n = nc * std::exp(arg_n);
            const double p = nv * std::exp(arg_p);

            const double arg_d = std::clamp((e_f - e_d) / kt, -80.0, 80.0);
            const double arg_a = std::clamp((e_a - e_f) / kt, -80.0, 80.0);

            const double n_d_plus = cfg.n_d / (1.0 + 2.0 * std::exp(arg_d));
            const double n_a_minus = cfg.n_a / (1.0 + 4.0 * std::exp(arg_a));

            return (p + n_d_plus) - (n + n_a_minus);
        };

        double e_low = e_v - 0.5;
        double e_high = e_c + 0.5;
        double e_mid = (e_low + e_high) / 2.0;

        while ((e_high - e_low) > tolerance_ev) {
            e_mid = (e_low + e_high) / 2.0;
            if (residual(e_mid) > 0.0) {
                e_low = e_mid;
            } else {
                e_high = e_mid;
            }
        }

        const double n_final = nc * std::exp(-(e_c - e_mid) / kt);
        const double p_final = nv * std::exp(-(e_mid - e_v) / kt);
        const double nd_plus_final = cfg.n_d / (1.0 + 2.0 * std::exp((e_mid - e_d) / kt));
        const double na_minus_final = cfg.n_a / (1.0 + 4.0 * std::exp((e_a - e_mid) / kt));

        return CalculationResult{
            .e_v_ev = e_v,
            .e_c_ev = e_c,
            .e_g_ev = e_g,
            .e_f_ev = e_mid,
            .n_elec_cm3 = n_final,
            .p_hole_cm3 = p_final,
            .n_d_plus_cm3 = nd_plus_final,
            .n_a_minus_cm3 = na_minus_final
        };
    }
};

} // namespace physics

int main() {
    physics::SemiconductorConfig cfg_p{
        .temp_k = 300.0,
        .n_d = 0.0,
        .e_d_relative = 0.045,
        .n_a = 2.0e17, // p-тип Si, Na = 2e17 cm^-3
        .e_a_relative = 0.045
    };

    if (auto res = physics::FermiLevelSolver::solve(cfg_p)) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "--- Розрахунок Si p-типу (T = 300 K, Na = 2e17 cm^-3) ---\n";
        std::cout << "Ширина забороненої зони Eg = " << res->e_g_ev << " еВ\n";
        std::cout << "Рівень Фермі Ef = " << res->e_f_ev << " еВ (відносно Ev)\n";
        std::cout << "Відстань Ef - Ev = " << (res->e_f_ev - res->e_v_ev) << " еВ\n";
        std::cout << "Концентрація дірок p = " << std::scientific << res->p_hole_cm3 << " см^-3\n";
    }

    return 0;
}
