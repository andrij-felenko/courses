// quantum_well_solver.cpp — Ідіоматичний чисельний солвер на C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <format>

namespace quantum {

constexpr double HBAR_J_S = 1.054571817e-34;
constexpr double M0_KG = 9.1093837015e-31;
constexpr double EV_TO_J = 1.602176634e-19;

struct GridConfig {
    std::size_t N{501};
    double window_width{30.0e-9}; // 30 нм
    double well_width{10.0e-9};   // 10 нм
    double V_barrier{0.224};      // 224 меВ
    double m_well{0.067};         // GaAs
    double m_barrier{0.092};      // AlGaAs
    double electric_field{0.0};   // В/м (для ефекту Штарка)
};

class QuantumWellSolver {
public:
    explicit QuantumWellSolver(GridConfig config)
        : cfg_(config), dz_(config.window_width / static_cast<double>(config.N - 1)) {
        initialize_grid();
        build_hamiltonian();
    }

    [[nodiscard]] std::expected<std::pair<double, std::vector<double>>, std::string>
    solve_ground_state(double E_guess = 0.05, std::size_t max_iter = 1000, double tol = 1e-7) const {
        std::size_t N = cfg_.N;
        std::vector<double> psi(N, 0.0);
        std::vector<double> rhs(N, 0.0);

        for (std::size_t i = 1; i < N - 1; ++i) {
            psi[i] = std::sin(std::numbers::pi * static_cast<double>(i) / static_cast<double>(N - 1));
            rhs[i] = psi[i];
        }

        double E_old = 0.0;
        double E_new = 0.0;

        for (std::size_t iter = 0; iter < max_iter; ++iter) {
            std::vector<double> b(N, 0.0);
            for (std::size_t i = 1; i < N - 1; ++i) {
                b[i] = diag_[i] - E_guess;
            }

            if (!solve_thomas(subdiag_, b, subdiag_, rhs, psi)) {
                return std::unexpected("Помилка алгоритму Томаса: вироджена матриця.");
            }

            // Нормування хвильової функції
            double norm = 0.0;
            for (std::size_t i = 1; i < N - 1; ++i) {
                norm += psi[i] * psi[i] * dz_;
            }
            norm = std::sqrt(norm);
            for (std::size_t i = 1; i < N - 1; ++i) {
                psi[i] /= norm;
            }

            // Відношення Релея
            E_new = 0.0;
            for (std::size_t i = 1; i < N - 1; ++i) {
                double H_psi = diag_[i] * psi[i] + subdiag_[i-1] * psi[i-1] + subdiag_[i] * psi[i+1];
                E_new += psi[i] * H_psi * dz_;
            }

            if (std::abs(E_new - E_old) < tol) {
                return std::make_pair(E_new, psi);
            }
            E_old = E_new;
            rhs = psi;
        }

        return std::make_pair(E_new, psi);
    }

private:
    GridConfig cfg_;
    double dz_;
    std::vector<double> z_;
    std::vector<double> V_;
    std::vector<double> m_eff_;
    std::vector<double> diag_;
    std::vector<double> subdiag_;

    void initialize_grid() {
        z_.resize(cfg_.N);
        V_.resize(cfg_.N);
        m_eff_.resize(cfg_.N);
        diag_.resize(cfg_.N);
        subdiag_.resize(cfg_.N);

        for (std::size_t i = 0; i < cfg_.N; ++i) {
            z_[i] = -cfg_.window_width / 2.0 + static_cast<double>(i) * dz_;
            if (std::abs(z_[i]) <= cfg_.well_width / 2.0) {
                V_[i] = 0.0;
                m_eff_[i] = cfg_.m_well;
            } else {
                V_[i] = cfg_.V_barrier;
                m_eff_[i] = cfg_.m_barrier;
            }
        }
    }

    void build_hamiltonian() {
        double C0 = (HBAR_J_S * HBAR_J_S) / (2.0 * M0_KG * dz_ * dz_ * EV_TO_J);
        for (std::size_t i = 1; i < cfg_.N - 1; ++i) {
            double m_left  = 0.5 * (m_eff_[i-1] + m_eff_[i]);
            double m_right = 0.5 * (m_eff_[i]   + m_eff_[i+1]);
            double A_i = C0 / m_left;
            double C_i = C0 / m_right;
            double V_field = cfg_.electric_field * z_[i];
            diag_[i] = A_i + C_i + V_[i] + V_field;
            subdiag_[i] = -C_i;
        }
    }

    static bool solve_thomas(std::span<const double> a, std::span<const double> b,
                             std::span<const double> c, std::span<const double> rhs,
                             std::span<double> x) {
        std::size_t N = b.size();
        std::vector<double> cp(N, 0.0);
        std::vector<double> dp(N, 0.0);

        if (std::abs(b[1]) < 1e-12) return false;
        cp[1] = c[1] / b[1];
        dp[1] = rhs[1] / b[1];

        for (std::size_t i = 2; i < N - 1; ++i) {
            double denom = b[i] - a[i] * cp[i-1];
            if (std::abs(denom) < 1e-12) return false;
            cp[i] = c[i] / denom;
            dp[i] = (rhs[i] - a[i] * dp[i-1]) / denom;
        }

        x[N-2] = dp[N-2];
        for (std::int64_t i = static_cast<std::int64_t>(N) - 3; i >= 1; --i) {
            x[i] = dp[i] - cp[i] * x[i+1];
        }
        return true;
    }
};

} // namespace quantum

int main() {
    quantum::GridConfig config;
    quantum::QuantumWellSolver solver(config);

    auto result = solver.solve_ground_state();
    if (result) {
        auto [E1, psi] = *result;
        std::cout << std::format("--- РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ КВАНТОВОЇ ЯМИ (C++20) ---\n");
        std::cout << std::format("Ширина ями: {:.1f} нм\n", config.well_width * 1e9);
        std::cout << std::format("Енергія основного стану E_1: {:.3f} меВ\n", E1 * 1000.0);
    } else {
        std::cerr << "Помилка обчислення: " << result.error() << '\n';
    }
    return 0;
}
