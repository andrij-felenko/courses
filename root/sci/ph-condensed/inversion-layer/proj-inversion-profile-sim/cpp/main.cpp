#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <expected>
#include <string>
#include <span>

namespace mos_physics {

struct PhysicalConstants {
    static constexpr double q_elem = 1.602176634e-19;    // C
    static constexpr double kb = 1.380649e-23;           // J/K
    static constexpr double eps0 = 8.8541878128e-14;     // F/cm
    static constexpr double eps_si = 11.7 * eps0;
    static constexpr double eps_ox = 3.9 * eps0;
    static constexpr double n_i = 1.5e10;                // cm^-3 at 300K
};

struct SimConfig {
    double v_g = 2.5;
    double n_a = 1e16;
    double d_ox_nm = 5.0;
    double temp_k = 300.0;
    double v_fb = 0.0;
    double x_max_nm = 20.0;
    double dx_nm = 0.05;
};

struct SimResult {
    double psi_s = 0.0;
    double psi_b = 0.0;
    double q_n = 0.0;
    std::vector<double> x_nm;
    std::vector<double> psi;
    std::vector<double> n_conc;
    std::vector<double> p_conc;
};

enum class SimError {
    InvalidParameters,
    ConvergenceFailed
};

class MosSolver {
private:
    SimConfig cfg_;
    double vt_;
    double psi_b_;
    double c_ox_;
    double l_d_;

    [[nodiscard]] double calculate_field(double psi_s) const noexcept {
        if (psi_s <= 0.0) return 0.0;
        const double u_s = psi_s / vt_;
        const double ratio = PhysicalConstants::n_i / cfg_.n_a;
        const double term1 = std::exp(-u_s) + u_s - 1.0;
        const double term2 = (ratio * ratio) * (std::exp(u_s) - u_s - 1.0);
        const double f_val = std::sqrt(std::max(0.0, term1 + term2));
        return (std::sqrt(2.0) * vt_ / l_d_) * f_val;
    }

    [[nodiscard]] double gate_residual(double psi_s) const noexcept {
        const double f_s = calculate_field(psi_s);
        const double q_sc = -PhysicalConstants::eps_si * f_s;
        const double v_g_calc = cfg_.v_fb + psi_s + (std::abs(q_sc) / c_ox_);
        return v_g_calc - cfg_.v_g;
    }

public:
    explicit MosSolver(SimConfig cfg) : cfg_(std::move(cfg)) {
        vt_ = (PhysicalConstants::kb * cfg_.temp_k) / PhysicalConstants::q_elem;
        psi_b_ = vt_ * std::log(cfg_.n_a / PhysicalConstants::n_i);
        c_ox_ = PhysicalConstants::eps_ox / (cfg_.d_ox_nm * 1e-7);
        l_d_ = std::sqrt((PhysicalConstants::eps_si * vt_) / (2.0 * PhysicalConstants::q_elem * cfg_.n_a));
    }

    [[nodiscard]] std::expected<SimResult, SimError> execute() const {
        if (cfg_.v_g < 0.0 || cfg_.n_a <= 0.0 || cfg_.d_ox_nm <= 0.0) {
            return std::unexpected(SimError::InvalidParameters);
        }

        // 1. Root finding via Bisection method
        double low = 0.0001;
        double high = std::max(0.1, cfg_.v_g);
        for (int iter = 0; iter < 80; ++iter) {
            double mid = 0.5 * (low + high);
            if (gate_residual(mid) > 0.0) {
                high = mid;
            } else {
                low = mid;
            }
        }
        const double psi_s_sol = 0.5 * (low + high);
        const double f_s_init = calculate_field(psi_s_sol);

        // 2. Numerical integration via RK4
        SimResult res;
        res.psi_s = psi_s_sol;
        res.psi_b = psi_b_;

        const double dx_cm = cfg_.dx_nm * 1e-7;
        const std::size_t n_steps = static_cast<std::size_t>(cfg_.x_max_nm / cfg_.dx_nm);

        res.x_nm.reserve(n_steps + 1);
        res.psi.reserve(n_steps + 1);
        res.n_conc.reserve(n_steps + 1);
        res.p_conc.reserve(n_steps + 1);

        double curr_psi = psi_s_sol;
        double curr_f = f_s_init;

        auto rhs_psi = [](double f) noexcept { return -f; };
        auto rhs_f = [this](double psi) noexcept {
            if (psi <= 0.0) return 0.0;
            const double u = psi / vt_;
            const double p_c = cfg_.n_a * std::exp(-u);
            const double n_c = (PhysicalConstants::n_i * PhysicalConstants::n_i / cfg_.n_a) * std::exp(u);
            const double rho = PhysicalConstants::q_elem * (p_c - n_c - cfg_.n_a);
            return -rho / PhysicalConstants::eps_si;
        };

        for (std::size_t i = 0; i <= n_steps; ++i) {
            const double x_nm = i * cfg_.dx_nm;
            res.x_nm.push_back(x_nm);
            res.psi.push_back(curr_psi);

            const double u = (curr_psi > 0.0) ? curr_psi / vt_ : 0.0;
            const double n_val = (PhysicalConstants::n_i * PhysicalConstants::n_i / cfg_.n_a) * std::exp(u);
            const double p_val = (curr_psi > 0.0) ? cfg_.n_a * std::exp(-u) : cfg_.n_a;
            res.n_conc.push_back(n_val);
            res.p_conc.push_back(p_val);

            // RK4 steps
            const double k1_psi = rhs_psi(curr_f);
            const double k1_f   = rhs_f(curr_psi);

            const double k2_psi = rhs_psi(curr_f + 0.5 * dx_cm * k1_f);
            const double k2_f   = rhs_f(curr_psi + 0.5 * dx_cm * k1_psi);

            const double k3_psi = rhs_psi(curr_f + 0.5 * dx_cm * k2_f);
            const double k3_f   = rhs_f(curr_psi + 0.5 * dx_cm * k2_psi);

            const double k4_psi = rhs_psi(curr_f + dx_cm * k3_f);
            const double k4_f   = rhs_f(curr_psi + dx_cm * k3_psi);

            curr_psi += (dx_cm / 6.0) * (k1_psi + 2.0 * k2_psi + 2.0 * k3_psi + k4_psi);
            curr_f   += (dx_cm / 6.0) * (k1_f + 2.0 * k2_f + 2.0 * k3_f + k4_f);

            if (curr_psi < 0.0) curr_psi = 0.0;
        }

        // 3. Integration of mobile inversion charge Q_n
        const double n_0 = (PhysicalConstants::n_i * PhysicalConstants::n_i) / cfg_.n_a;
        res.q_n = 0.0;
        for (std::size_t i = 0; i < res.n_conc.size() - 1; ++i) {
            if (res.n_conc[i] > cfg_.n_a) {
                const double avg_n = 0.5 * (res.n_conc[i] + res.n_conc[i + 1]) - n_0;
                res.q_n += PhysicalConstants::q_elem * avg_n * dx_cm;
            }
        }

        return res;
    }
};

} // namespace mos_physics

int main() {
    mos_physics::SimConfig config;
    config.v_g = 2.5;
    config.n_a = 1e16;
    config.d_ox_nm = 5.0;

    mos_physics::MosSolver solver(config);
    auto outcome = solver.execute();

    if (!outcome) {
        std::cerr << "Помилка симуляції МДН-структури.\n";
        return 1;
    }

    const auto& res = outcome.value();
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "--- Результати симуляції (C++20) ---\n";
    std::cout << "Поверхневий потенціал psi_s = " << res.psi_s << " В\n";
    std::cout << "Об'ємний потенціал Фермі psi_b = " << res.psi_b << " В\n";
    std::cout << "Поріг сильної інверсії 2*psi_b = " << 2.0 * res.psi_b << " В\n";
    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Інверсійний заряд Q_n = " << res.q_n << " Кл/см²\n\n";

    std::cout << "Профіль біля поверхні (перші 5 вузлів):\n";
    for (std::size_t i = 0; i < 5 && i < res.x_nm.size(); ++i) {
        std::cout << "  x = " << std::fixed << std::setprecision(2) << res.x_nm[i]
                  << " нм: ψ = " << res.psi[i]
                  << " В, n = " << std::scientific << res.n_conc[i] << " см⁻³\n";
    }

    return 0;
}
