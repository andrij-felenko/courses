// lyapunov_lorenz.cpp - Чисельний розрахунок спектра Ляпунова мовою C++20
#include <iostream>
#include <array>
#include <vector>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <span>

namespace lyapunov {

constexpr std::size_t Dim = 3;

struct LorenzParams {
    double sigma{10.0};
    double rho{28.0};
    double beta{8.0 / 3.0};
};

using State = std::array<double, Dim>;
using Matrix = std::array<std::array<double, Dim>, Dim>;

class LorenzSystem {
public:
    explicit LorenzSystem(LorenzParams params) : params_(params) {}

    [[nodiscard]] State rhs(const State& x) const noexcept {
        return {
            params_.sigma * (x[1] - x[0]),
            x[0] * (params_.rho - x[2]) - x[1],
            x[0] * x[1] - params_.beta * x[2]
        };
    }

    [[nodiscard]] Matrix jacobian(const State& x) const noexcept {
        return Matrix{{
            {-params_.sigma, params_.sigma, 0.0},
            {params_.rho - x[2], -1.0, -x[0]},
            {x[1], x[0], -params_.beta}
        }};
    }

private:
    LorenzParams params_;
};

class LyapunovSolver {
public:
    LyapunovSolver(LorenzSystem sys, double dt) : sys_(sys), dt_(dt) {}

    struct Result {
        std::array<double, Dim> spectrum;
        double kaplan_yorke_dim;
    };

    Result compute(State start_state, std::size_t total_steps, std::size_t transient_steps) {
        State x = start_state;
        Matrix Q{};
        for (std::size_t i = 0; i < Dim; ++i) Q[i][i] = 1.0;

        // Пропуск перехідного процесу
        for (std::size_t step = 0; step < transient_steps; ++step) {
            rk4_step(x, Q);
            gram_schmidt(Q);
        }

        std::array<double, Dim> lyap_sum{0.0, 0.0, 0.0};

        // Основний цикл
        for (std::size_t step = 0; step < total_steps; ++step) {
            rk4_step(x, Q);
            auto r_diag = gram_schmidt(Q);
            for (std::size_t i = 0; i < Dim; ++i) {
                lyap_sum[i] += std::log(r_diag[i]);
            }
        }

        double total_time = static_cast<double>(total_steps) * dt_;
        Result res{};
        for (std::size_t i = 0; i < Dim; ++i) {
            res.spectrum[i] = lyap_sum[i] / total_time;
        }

        double l1 = res.spectrum[0];
        double l2 = res.spectrum[1];
        double l3 = res.spectrum[2];
        if (l1 > 0.0 && (l1 + l2) > 0.0 && l3 < 0.0) {
            res.kaplan_yorke_dim = 2.0 + (l1 + l2) / std::abs(l3);
        } else {
            res.kaplan_yorke_dim = 0.0;
        }

        return res;
    }

private:
    static State mat_vec(const Matrix& J, const State& y) noexcept {
        State res{};
        for (std::size_t i = 0; i < Dim; ++i) {
            for (std::size_t j = 0; j < Dim; ++j) {
                res[i] += J[i][j] * y[j];
            }
        }
        return res;
    }

    void rk4_step(State& x, Matrix& Q) const {
        auto step_k = [this](const State& st, const Matrix& q_mat) {
            State dxdt = sys_.rhs(st);
            Matrix J = sys_.jacobian(st);
            Matrix dqdt{};
            for (std::size_t col = 0; col < Dim; ++col) {
                State col_v{q_mat[0][col], q_mat[1][col], q_mat[2][col]};
                State res = mat_vec(J, col_v);
                for (std::size_t r = 0; r < Dim; ++r) dqdt[r][col] = res[r];
            }
            return std::make_pair(dxdt, dqdt);
        };

        auto [k1_x, k1_Q] = step_k(x, Q);

        State x2{}; Matrix Q2{};
        for (std::size_t i = 0; i < Dim; ++i) x2[i] = x[i] + 0.5 * dt_ * k1_x[i];
        for (std::size_t r = 0; r < Dim; ++r)
            for (std::size_t c = 0; c < Dim; ++c)
                Q2[r][c] = Q[r][c] + 0.5 * dt_ * k1_Q[r][c];

        auto [k2_x, k2_Q] = step_k(x2, Q2);

        State x3{}; Matrix Q3{};
        for (std::size_t i = 0; i < Dim; ++i) x3[i] = x[i] + 0.5 * dt_ * k2_x[i];
        for (std::size_t r = 0; r < Dim; ++r)
            for (std::size_t c = 0; c < Dim; ++c)
                Q3[r][c] = Q[r][c] + 0.5 * dt_ * k2_Q[r][c];

        auto [k3_x, k3_Q] = step_k(x3, Q3);

        State x4{}; Matrix Q4{};
        for (std::size_t i = 0; i < Dim; ++i) x4[i] = x[i] + dt_ * k3_x[i];
        for (std::size_t r = 0; r < Dim; ++r)
            for (std::size_t c = 0; c < Dim; ++c)
                Q4[r][c] = Q[r][c] + dt_ * k3_Q[r][c];

        auto [k4_x, k4_Q] = step_k(x4, Q4);

        for (std::size_t i = 0; i < Dim; ++i) {
            x[i] += (dt_ / 6.0) * (k1_x[i] + 2.0 * k2_x[i] + 2.0 * k3_x[i] + k4_x[i]);
        }
        for (std::size_t r = 0; r < Dim; ++r) {
            for (std::size_t c = 0; c < Dim; ++c) {
                Q[r][c] += (dt_ / 6.0) * (k1_Q[r][c] + 2.0 * k2_Q[r][c] + 2.0 * k3_Q[r][c] + k4_Q[r][c]);
            }
        }
    }

    std::array<double, Dim> gram_schmidt(Matrix& Q) const {
        std::array<double, Dim> r_diag{};
        for (std::size_t j = 0; j < Dim; ++j) {
            State v{Q[0][j], Q[1][j], Q[2][j]};
            for (std::size_t k = 0; k < j; ++k) {
                double dot = 0.0;
                for (std::size_t i = 0; i < Dim; ++i) dot += v[i] * Q[i][k];
                for (std::size_t i = 0; i < Dim; ++i) v[i] -= dot * Q[i][k];
            }
            double norm = 0.0;
            for (std::size_t i = 0; i < Dim; ++i) norm += v[i] * v[i];
            norm = std::sqrt(norm);
            r_diag[j] = norm;

            for (std::size_t i = 0; i < Dim; ++i) {
                Q[i][j] = (norm > 1e-14) ? (v[i] / norm) : 0.0;
            }
        }
        return r_diag;
    }

    LorenzSystem sys_;
    double dt_;
};

} // namespace lyapunov

int main() {
    using namespace lyapunov;
    LorenzSystem lorenz{LorenzParams{.sigma = 10.0, .rho = 28.0, .beta = 8.0 / 3.0}};
    LyapunovSolver solver{lorenz, 0.01};

    auto result = solver.compute({1.0, 1.0, 1.0}, 100000, 10000);

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Спектр показників Ляпунова (C++20):\n";
    for (std::size_t i = 0; i < Dim; ++i) {
        std::cout << "  λ_" << (i + 1) << " = " << (result.spectrum[i] >= 0 ? "+" : "") << result.spectrum[i] << "\n";
    }
    std::cout << "Розмірність Каплана–Йорке D_L = " << result.kaplan_yorke_dim << "\n";

    return 0;
}
