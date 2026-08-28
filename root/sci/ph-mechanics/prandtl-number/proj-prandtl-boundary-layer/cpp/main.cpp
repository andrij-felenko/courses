#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <array>
#include <span>

namespace fluid_physics {

struct State {
    double eta{0.0};
    double f{0.0};
    double fp{0.0};
    double fpp{0.0};
    double theta{0.0};
    double thetap{0.0};
};

struct BoundaryLayerResult {
    double prandtl{0.71};
    double wall_shear_fpp0{0.33206};
    double wall_heat_thetap0{0.33206};
    double eta_delta_v{4.91};
    double eta_delta_t{4.91};
    double thickness_ratio{1.0};
    double nusselt_scaling{0.33206};
};

class BlasiusPohlhausenSolver {
public:
    explicit BlasiusPohlhausenSolver(double prandtl, std::size_t steps = 2000)
        : m_prandtl(prandtl), m_steps(steps) {
        m_eta_max = (prandtl < 0.1) ? (12.0 / std::sqrt(prandtl)) : 10.0;
    }

    [[nodiscard]] BoundaryLayerResult solve() const {
        BoundaryLayerResult result{};
        result.prandtl = m_prandtl;

        // 1. Стрільба гідродинамічна: шукаємо f''(0)
        const double f_pp_0 = shoot_hydrodynamics();
        result.wall_shear_fpp0 = f_pp_0;

        // 2. Стрільба теплова: шукаємо theta'(0)
        const double theta_p_0 = shoot_thermal(f_pp_0);
        result.wall_heat_thetap0 = theta_p_0;
        result.nusselt_scaling = theta_p_0;

        // 3. Побудова профілю та пошук товщин шарів
        const auto profile = integrate_full_profile(f_pp_0, theta_p_0);
        
        result.eta_delta_v = m_eta_max;
        result.eta_delta_t = m_eta_max;

        for (const auto& st : profile) {
            if (st.fp >= 0.99 && result.eta_delta_v == m_eta_max) {
                result.eta_delta_v = st.eta;
            }
            if (st.theta >= 0.99 && result.eta_delta_t == m_eta_max) {
                result.eta_delta_t = st.eta;
            }
        }
        result.thickness_ratio = result.eta_delta_v / result.eta_delta_t;

        return result;
    }

private:
    using Vector5 = std::array<double, 5>;

    static Vector5 derivatives(double pr, const Vector5& y) noexcept {
        return {y[1], y[2], -0.5 * y[0] * y[2], y[4], -0.5 * pr * y[0] * y[4]};
    }

    static Vector5 rk4_step(double pr, double h, Vector5 y) noexcept {
        const auto k1 = derivatives(pr, y);
        
        Vector5 y_tmp{};
        for (std::size_t i = 0; i < 5; ++i) y_tmp[i] = y[i] + 0.5 * h * k1[i];
        const auto k2 = derivatives(pr, y_tmp);

        for (std::size_t i = 0; i < 5; ++i) y_tmp[i] = y[i] + 0.5 * h * k2[i];
        const auto k3 = derivatives(pr, y_tmp);

        for (std::size_t i = 0; i < 5; ++i) y_tmp[i] = y[i] + h * k3[i];
        const auto k4 = derivatives(pr, y_tmp);

        Vector5 y_next{};
        for (std::size_t i = 0; i < 5; ++i) {
            y_next[i] = y[i] + (h / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
        return y_next;
    }

    double shoot_hydrodynamics() const {
        auto eval_err = [this](double s) {
            const double h = m_eta_max / static_cast<double>(m_steps);
            Vector5 y{0.0, 0.0, s, 0.0, 1.0};
            for (std::size_t i = 0; i < m_steps; ++i) {
                y = rk4_step(m_prandtl, h, y);
            }
            return y[1] - 1.0;
        };

        double s0 = 0.2, s1 = 0.5;
        double e0 = eval_err(s0), e1 = eval_err(s1);

        for (std::size_t iter = 0; iter < 100; ++iter) {
            if (std::abs(e1) < 1e-8) break;
            double s_next = s1 - e1 * (s1 - s0) / (e1 - e0);
            s0 = s1; e0 = e1;
            s1 = s_next; e1 = eval_err(s1);
        }
        return s1;
    }

    double shoot_thermal(double fpp0) const {
        auto eval_err = [this, fpp0](double st) {
            const double h = m_eta_max / static_cast<double>(m_steps);
            Vector5 y{0.0, 0.0, fpp0, 0.0, st};
            for (std::size_t i = 0; i < m_steps; ++i) {
                y = rk4_step(m_prandtl, h, y);
            }
            return y[3] - 1.0;
        };

        double st0 = 0.1, st1 = 1.0;
        double e0 = eval_err(st0), e1 = eval_err(st1);

        for (std::size_t iter = 0; iter < 100; ++iter) {
            if (std::abs(e1) < 1e-8) break;
            double st_next = st1 - e1 * (st1 - st0) / (e1 - e0);
            st0 = st1; e0 = e1;
            st1 = st_next; e1 = eval_err(st1);
        }
        return st1;
    }

    std::vector<State> integrate_full_profile(double fpp0, double thetap0) const {
        std::vector<State> profile;
        profile.reserve(m_steps + 1);

        const double h = m_eta_max / static_cast<double>(m_steps);
        Vector5 y{0.0, 0.0, fpp0, 0.0, thetap0};

        profile.push_back({0.0, y[0], y[1], y[2], y[3], y[4]});
        for (std::size_t i = 1; i <= m_steps; ++i) {
            y = rk4_step(m_prandtl, h, y);
            profile.push_back({i * h, y[0], y[1], y[2], y[3], y[4]});
        }
        return profile;
    }

    double m_prandtl;
    std::size_t m_steps;
    double m_eta_max;
};

} // namespace fluid_physics

int main() {
    const std::vector<double> test_prandtl = {0.005, 0.025, 0.71, 7.0, 100.0};

    std::cout << "=== Обчислення примежового шару Блазіуса-Польгаузена (C++20) ===\n";
    std::cout << std::setw(8) << "Pr"
              << std::setw(12) << "f''(0)"
              << std::setw(12) << "θ'(0)"
              << std::setw(10) << "η_δv"
              << std::setw(10) << "η_δt"
              << std::setw(12) << "δv/δt" << "\n";
    std::cout << std::string(64, '-') << "\n";

    for (double pr : test_prandtl) {
        fluid_physics::BlasiusPohlhausenSolver solver(pr);
        auto res = solver.solve();

        std::cout << std::fixed << std::setprecision(3)
                  << std::setw(8) << res.prandtl
                  << std::setprecision(5)
                  << std::setw(12) << res.wall_shear_fpp0
                  << std::setw(12) << res.wall_heat_thetap0
                  << std::setprecision(2)
                  << std::setw(10) << res.eta_delta_v
                  << std::setw(10) << res.eta_delta_t
                  << std::setprecision(3)
                  << std::setw(12) << res.thickness_ratio << "\n";
    }

    return 0;
}
