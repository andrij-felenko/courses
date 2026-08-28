#include <iostream>
#include <cmath>
#include <iomanip>
#include <string>
#include <algorithm>

// ── Фізичні фундаментальні константи ──────────────────────────────────────────
constexpr double K_B_KEV = 8.617333e-8;          // Стала Больцмана (кЕв / К)
constexpr double COULOMB_CONST_KEV_FM = 1439.96;  // e^2 / (4pi eps0) (кЕв * фм)
constexpr double R0_FM = 1.25;                    // Радіус нуклона (фм)

struct ReactionParams {
    std::string name;
    int z1;
    double a1;
    int z2;
    double a2;
    double temp_kelvin;
};

struct SimulationResult {
    double mu_amu;
    double r_collision_fm;
    double v_barrier_mev;
    double b_gamow;
    double kb_t_kev;
    double e0_theory_kev;
    double e0_numerical_kev;
    double delta_e_kev;
    double p_at_e0;
    double tau;
    double integral_rate;
};

class CoulombSolver {
public:
    static SimulationResult solve(const ReactionParams& p) {
        SimulationResult res{};
        
        // Зведена маса ядер
        res.mu_amu = (p.a1 * p.a2) / (p.a1 + p.a2);
        
        // Радіус ядерного зіткнення
        res.r_collision_fm = R0_FM * (std::pow(p.a1, 1.0 / 3.0) + std::pow(p.a2, 1.0 / 3.0));
        
        // Висота кулонівського бар'єра
        const double v_barrier_kev = (p.z1 * p.z2 * COULOMB_CONST_KEV_FM) / res.r_collision_fm;
        res.v_barrier_mev = v_barrier_kev / 1000.0;
        
        // Астрофізична стала Ґамова
        res.b_gamow = 31.291 * p.z1 * p.z2 * std::sqrt(res.mu_amu);
        
        // Теплова енергія
        res.kb_t_kev = K_B_KEV * p.temp_kelvin;
        
        // Теоретична енергія піку Ґамова та його ширина
        res.e0_theory_kev = std::pow((res.b_gamow * res.kb_t_kev) / 2.0, 2.0 / 3.0);
        res.delta_e_kev = 4.0 * std::sqrt((res.e0_theory_kev * res.kb_t_kev) / 3.0);
        
        // Межі чисельного інтегрування
        const double e_min = std::max(0.01, res.e0_theory_kev - 3.5 * res.delta_e_kev);
        const double e_max = res.e0_theory_kev + 4.5 * res.delta_e_kev;
        const int steps = 2000;
        const double de = (e_max - e_min) / steps;
        
        double max_val = 0.0;
        res.e0_numerical_kev = res.e0_theory_kev;
        double integral_sum = 0.0;
        
        for (int i = 0; i <= steps; ++i) {
            const double e_val = e_min + i * de;
            const double log_integrand = std::log(e_val) - (e_val / res.kb_t_kev) - (res.b_gamow / std::sqrt(e_val));
            
            double val = 0.0;
            if (log_integrand > -300.0) {
                val = std::exp(log_integrand);
            }
            
            if (val > max_val) {
                max_val = val;
                res.e0_numerical_kev = e_val;
            }
            
            const double weight = (i == 0 || i == steps) ? 0.5 : 1.0;
            integral_sum += val * weight * de;
        }
        
        res.p_at_e0 = std::exp(-res.b_gamow / std::sqrt(res.e0_numerical_kev));
        res.tau = 3.0 * res.e0_numerical_kev / res.kb_t_kev;
        res.integral_rate = integral_sum;
        
        return res;
    }
};

void print_result(const ReactionParams& p, const SimulationResult& res) {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== " << p.name << " (T = " << p.temp_kelvin / 1e6 << " млн К) ===\n";
    std::cout << " Зведена маса μ:             " << res.mu_amu << " а.о.м.\n";
    std::cout << " Радіус зіткнення R:         " << res.r_collision_fm << " фм\n";
    std::cout << " Висота бар'єра V_B:         " << res.v_barrier_mev << " МеВ (" << res.v_barrier_mev * 1000.0 << " кЕв)\n";
    std::cout << " Стала Ґамова b_G:           " << res.b_gamow << " кЕв¹/²\n";
    std::cout << " Теплова енергія k_B T:      " << res.kb_t_kev << " кЕв\n";
    std::cout << " Енергія піку Ґамова E₀:     " << res.e0_numerical_kev << " кЕв\n";
    std::cout << " Ефективна ширина ΔE:        " << res.delta_e_kev << " кЕв\n";
    std::cout << " Подавлення exp(-τ):         " << std::scientific << std::exp(-res.tau) << " (τ = " << std::fixed << res.tau << ")\n";
    std::cout << " Прозорість P(E₀):           " << std::scientific << res.p_at_e0 << "\n\n";
}

int main() {
    ReactionParams p_pp{"Протон-протонний синтез (p + p)", 1, 1.0078, 1, 1.0078, 15.7e6};
    print_result(p_pp, CoulombSolver::solve(p_pp));

    ReactionParams p_dt{"Дейтерій-тритієвий синтез (d + t)", 1, 2.0141, 1, 3.0160, 100.0e6};
    print_result(p_dt, CoulombSolver::solve(p_dt));

    ReactionParams p_pb{"Протон-борний синтез (p + ¹¹B)", 1, 1.0078, 5, 11.0093, 300.0e6};
    print_result(p_pb, CoulombSolver::solve(p_pb));

    return 0;
}
