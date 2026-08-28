#ifndef LANDAU_SOLVER_HPP
#define LANDAU_SOLVER_HPP

#include <cmath>
#include <vector>
#include <string>
#include <optional>
#include <stdexcept>

namespace landau {

enum class TransitionType {
    SECOND_ORDER,
    FIRST_ORDER,
    TRICRITICAL
};

enum class ErrorCode {
    SUCCESS = 0,
    CONVERGENCE_FAILED = 1,
    INVALID_PARAMETERS = 2,
    UNSTABLE_POTENTIAL = 3
};

struct LandauParams {
    double a0 = 1.0;
    double b = 1.0;
    double c = 0.0;
    double Tc = 300.0;
    double g = 1.0e-18;
    double C0 = 25.0;
    TransitionType type = TransitionType::SECOND_ORDER;

    bool validate() const {
        if (Tc <= 0.0 || a0 <= 0.0) return false;
        if (type == TransitionType::SECOND_ORDER && b <= 0.0) return false;
        if (type == TransitionType::FIRST_ORDER && (b >= 0.0 || c <= 0.0)) return false;
        if (type == TransitionType::TRICRITICAL && c <= 0.0) return false;
        return true;
    }
};

struct StateResult {
    double T = 0.0;
    double H = 0.0;
    double eta = 0.0;
    double free_energy = 0.0;
    double heat_capacity = 0.0;
    double susceptibility = 0.0;
    double correlation_length = 0.0;
    ErrorCode error = ErrorCode::SUCCESS;
};

class LandauSolver {
private:
    LandauParams params;
    double max_iterations = 200;
    double tolerance = 1.0e-9;

public:
    explicit LandauSolver(const LandauParams& p) : params(p) {
        if (!params.validate()) {
            throw std::invalid_argument("Некоректні параметри потенціалу Ландау");
        }
    }

    // Обчислення термодинамічного потенціалу Phi(T, eta, H)
    [[nodiscard]] double compute_potential(double T, double eta, double H = 0.0) const noexcept {
        double a = params.a0 * (T - params.Tc);
        double energy = a * eta * eta + 0.5 * params.b * std::pow(eta, 4) - eta * H;
        if (params.c > 0.0) {
            energy += (1.0 / 3.0) * params.c * std::pow(eta, 6);
        }
        return energy;
    }

    // Пошук рівноважного параметра порядку методом Ньютона — Рафсона
    [[nodiscard]] double compute_order_parameter(double T, double H = 0.0, double eta_guess = 0.0) const {
        if (params.type == TransitionType::SECOND_ORDER && T >= params.Tc && std::abs(H) < 1.0e-12) {
            return 0.0;
        }

        double a = params.a0 * (T - params.Tc);
        double eta = eta_guess;

        if (eta == 0.0 && T < params.Tc && params.type == TransitionType::SECOND_ORDER) {
            eta = std::sqrt(params.a0 * (params.Tc - T) / params.b);
        }

        for (int iter = 0; iter < max_iterations; ++iter) {
            double grad = 2.0 * a * eta + 2.0 * params.b * std::pow(eta, 3) - H;
            double hessian = 2.0 * a + 6.0 * params.b * eta * eta;

            if (params.c > 0.0) {
                grad += 2.0 * params.c * std::pow(eta, 5);
                hessian += 10.0 * params.c * std::pow(eta, 4);
            }

            if (std::abs(hessian) < 1.0e-14) break;

            double step = grad / hessian;
            eta -= step;

            if (std::abs(step) < tolerance) {
                return eta;
            }
        }
        return eta;
    }

    // Обчислення ізобарної теплоємності Cp(T)
    [[nodiscard]] double compute_heat_capacity(double T) const noexcept {
        if (params.type == TransitionType::SECOND_ORDER) {
            if (T >= params.Tc) {
                return params.C0;
            } else {
                return params.C0 + (params.a0 * params.a0 * T) / params.b;
            }
        }
        return params.C0;
    }

    // Обчислення оборотної сприйнятливості chi(T)
    [[nodiscard]] double compute_susceptibility(double T, double H = 0.0) const {
        double eta = compute_order_parameter(T, H);
        double a = params.a0 * (T - params.Tc);
        double denom = 2.0 * a + 6.0 * params.b * eta * eta;
        if (params.c > 0.0) {
            denom += 10.0 * params.c * std::pow(eta, 4);
        }
        if (std::abs(denom) < 1.0e-12) {
            return 1.0e12; // Полюс поблизу Tc
        }
        return 1.0 / denom;
    }

    // Обчислення довжини кореляції xi(T)
    [[nodiscard]] double compute_correlation_length(double T, double H = 0.0) const {
        double chi = compute_susceptibility(T, H);
        if (chi <= 0.0) return 0.0;
        return std::sqrt(params.g * chi);
    }

    // Комплексний розрахунок термодинамічного стану
    [[nodiscard]] StateResult solve_state(double T, double H = 0.0) const {
        StateResult res;
        res.T = T;
        res.H = H;
        res.eta = compute_order_parameter(T, H);
        res.free_energy = compute_potential(res.T, res.eta, H);
        res.heat_capacity = compute_heat_capacity(T);
        res.susceptibility = compute_susceptibility(T, H);
        res.correlation_length = compute_correlation_length(T, H);
        res.error = ErrorCode::SUCCESS;
        return res;
    }
};

} // namespace landau

#endif // LANDAU_SOLVER_HPP
