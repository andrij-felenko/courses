// =========================================================================
// File: poincare_sec.hpp
// Description: C++20 Type-safe header-only API for Poincaré map
// =========================================================================

#ifndef POINCARE_SEC_HPP
#define POINCARE_SEC_HPP

#include <span>
#include <vector>
#include <concepts>
#include <expected>
#include <functional>
#include <cmath>
#include <limits>
#include <array>

namespace poincare {

/**
 * @brief Перелік чисельних помилок C++ API.
 */
enum class Status {
    Success,
    NullBuffer,
    InvalidDimension,
    InvalidParameters,
    IntegrationDivergence,
    MaxStepsExceeded,
    RootSearchFailed,
    NonTransversal
};

/**
 * @brief Концепт векторного поля фізичної системи: f(state, t, rhs_out).
 */
template <typename F, typename StateType>
concept SystemVectorField = requires(F f, const StateType& s, double t, StateType& out) {
    { f(s, t, out) } -> std::same_as<void>;
};

/**
 * @brief Концепт секущої поверхні: g(state, grad_out) -> double.
 */
template <typename G, typename StateType>
concept TransversalSection = requires(G g, const StateType& s, StateType& grad) {
    { g(s, grad) } -> std::same_as<double>;
};

/**
 * @brief Структура налаштувань обчислення у C++.
 */
struct SolverConfig {
    double rel_tol{1e-9};
    double abs_tol{1e-12};
    double initial_dt{1e-3};
    double min_dt{1e-14};
    double max_dt{1.0};
    std::size_t max_steps{1'000'000};
    bool enforce_direction{true};
};

/**
 * @brief Точка перерізу Пуанкаре у C++.
 */
template <std::size_t Dim>
struct SectionPoint {
    double time{0.0};
    std::array<double, Dim> state{};
    double return_time{0.0};
    std::size_t steps_executed{0};
};

/**
 * @brief Клас розв'язувача перерізу Пуанкаре C++20.
 */
template <std::size_t Dim, typename SystemRHS, typename SectionFunc>
    requires SystemVectorField<SystemRHS, std::array<double, Dim>> &&
             TransversalSection<SectionFunc, std::array<double, Dim>>
class MapSolver {
public:
    using State = std::array<double, Dim>;
    using Point = SectionPoint<Dim>;

    MapSolver(SystemRHS sys, SectionFunc sec, SolverConfig cfg = {})
        : system_(std::move(sys)), section_(std::move(sec)), config_(cfg) {}

    /**
     * @brief Обчислити наступну точку перетину секущої поверхні.
     */
    [[nodiscard]] std::expected<Point, Status> step(State current_state, double current_time) const {
        State x = current_state;
        double t = current_time;
        double dt = config_.initial_dt;

        State grad_g{};
        double g_prev = section_(x, grad_g);
        std::size_t step_cnt = 0;

        while (step_cnt < config_.max_steps) {
            State x_next{};
            rk4_step(x, t, dt, x_next);
            double t_next = t + dt;

            for (double val : x_next) {
                if (std::isnan(val) || std::isinf(val)) {
                    return std::unexpected(Status::IntegrationDivergence);
                }
            }

            double g_next = section_(x_next, grad_g);

            // Перевірка зміни знака секущої функції g(x)
            if (g_prev * g_next < 0.0) {
                // Перевірка трансверсальності
                State rhs_val{};
                system_(x_next, t_next, rhs_val);
                double dot_prod = 0.0;
                for (std::size_t i = 0; i < Dim; ++i) {
                    dot_prod += grad_g[i] * rhs_val[i];
                }

                if (!config_.enforce_direction || dot_prod > 0.0) {
                    // Уточнення кореня методом інтерполяції Ерміта
                    double s_star = find_root_hermite(x, x_next, t, dt, g_prev, g_next);
                    double t_star = t + s_star * dt;
                    State x_star = interpolate_hermite(x, x_next, t, dt, s_star);

                    return Point{
                        .time = t_star,
                        .state = x_star,
                        .return_time = t_star - current_time,
                        .steps_executed = step_cnt + 1
                    };
                }
            }

            x = x_next;
            t = t_next;
            g_prev = g_next;
            step_cnt++;
        }

        return std::unexpected(Status::MaxStepsExceeded);
    }

    /**
     * @brief Збір послідовності N точок перерізу.
     */
    [[nodiscard]] std::expected<std::vector<Point>, Status> compute_series(
        State start_state, 
        std::size_t num_points) const 
    {
        std::vector<Point> result;
        result.reserve(num_points);

        State current_x = start_state;
        double current_t = 0.0;

        for (std::size_t i = 0; i < num_points; ++i) {
            auto res = step(current_x, current_t);
            if (!res) {
                return std::unexpected(res.error());
            }
            result.push_back(*res);
            current_x = res->state;
            current_t = res->time;
        }

        return result;
    }

private:
    void rk4_step(const State& s, double t, double dt, State& out) const {
        State k1{}, k2{}, k3{}, k4{};
        State tmp{};

        system_(s, t, k1);

        for (std::size_t i = 0; i < Dim; ++i) tmp[i] = s[i] + 0.5 * dt * k1[i];
        system_(tmp, t + 0.5 * dt, k2);

        for (std::size_t i = 0; i < Dim; ++i) tmp[i] = s[i] + 0.5 * dt * k2[i];
        system_(tmp, t + 0.5 * dt, k3);

        for (std::size_t i = 0; i < Dim; ++i) tmp[i] = s[i] + dt * k3[i];
        system_(tmp, t + dt, k4);

        for (std::size_t i = 0; i < Dim; ++i) {
            out[i] = s[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
    }

    double find_root_hermite(const State& x1, const State& x2, double t1, double dt, double g1, double g2) const {
        double s_left = 0.0;
        double s_right = 1.0;
        State dummy_grad{};

        for (int iter = 0; iter < 10; ++iter) {
            double s_mid = 0.5 * (s_left + s_right);
            State x_mid = interpolate_hermite(x1, x2, t1, dt, s_mid);
            double g_mid = section_(x_mid, dummy_grad);

            if (g1 * g_mid < 0.0) {
                s_right = s_mid;
            } else {
                s_left = s_mid;
            }
        }
        return 0.5 * (s_left + s_right);
    }

    State interpolate_hermite(const State& x1, const State& x2, double t1, double dt, double s) const {
        State v1{}, v2{};
        system_(x1, t1, v1);
        system_(x2, t1 + dt, v2);

        double h00 = (1.0 - 3.0 * s * s + 2.0 * s * s * s);
        double h10 = s * (1.0 - s) * (1.0 - s);
        double h01 = s * s * (3.0 - 2.0 * s);
        double h11 = s * s * (s - 1.0);

        State res{};
        for (std::size_t i = 0; i < Dim; ++i) {
            res[i] = h00 * x1[i] + h10 * dt * v1[i] + h01 * x2[i] + h11 * dt * v2[i];
        }
        return res;
    }

    SystemRHS system_;
    SectionFunc section_;
    SolverConfig config_;
};

} // namespace poincare

#endif // POINCARE_SEC_HPP
