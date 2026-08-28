#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <span >

namespace physics {

struct JilesAthertonParams {
    double Ms{1.6e6};    // Намагніченість насичення (А/м)
    double a{800.0};     // Константа термічного поля (А/м)
    double alpha{1.1e-3};// Поле Вейса
    double k{500.0};     // Пиннинг дефектів
    double c{0.15};      // Коефіцієнт оборотності
};

struct HysteresisPoint {
    double H_field;
    double M_magnetization;
    double B_induction;
};

class HysteresisSimulator {
public:
    explicit HysteresisSimulator(JilesAthertonParams params) noexcept 
        : p_(params) {}

    [[nodiscard]] double langevin(double x) const noexcept {
        if (std::abs(x) < 1e-4) {
            return x / 3.0 - (x * x * x) / 45.0;
        }
        return (1.0 / std::tanh(x)) - (1.0 / x);
    }

    [[nodiscard]] double langevinDerivative(double x) const noexcept {
        if (std::abs(x) < 1e-4) {
            return 1.0 / 3.0 - (x * x) / 15.0;
        }
        const double ct = 1.0 / std::tanh(x);
        return 1.0 - ct * ct + 1.0 / (x * x);
    }

    [[nodiscard]] double computeMan(double H, double M) const noexcept {
        const double He = H + p_.alpha * M;
        if (std::abs(He) < 1e-9) return 0.0;
        return p_.Ms * langevin(He / p_.a);
    }

    [[nodiscard]] double computeDerivative(double H, double M, double dir) const noexcept {
        const double Man = computeMan(H, M);
        const double He = H + p_.alpha * M;
        const double dMan_dHe = (std::abs(He) < 1e-9) 
            ? (p_.Ms / (3.0 * p_.a)) 
            : (p_.Ms / p_.a) * langevinDerivative(He / p_.a);

        const double delta = (dir >= 0.0) ? 1.0 : -1.0;
        double den = delta * p_.k - p_.alpha * (Man - M);
        if (std::abs(den) < 1e-9) den = 1e-9;

        double dMirr_dH = (Man - M) / den;
        if ((dir > 0.0 && dMirr_dH < 0.0) || (dir < 0.0 && dMirr_dH > 0.0)) {
            dMirr_dH = 0.0;
        }

        return (dMirr_dH + p_.c * dMan_dHe) / (1.0 + p_.c * (1.0 - p_.alpha * dMan_dHe));
    }

    [[nodiscard]] double rk4Step(double H, double M, double dH) const noexcept {
        const double dir = (dH >= 0.0) ? 1.0 : -1.0;
        const double k1 = computeDerivative(H, M, dir);
        const double k2 = computeDerivative(H + 0.5 * dH, M + 0.5 * dH * k1, dir);
        const double k3 = computeDerivative(H + 0.5 * dH, M + 0.5 * dH * k2, dir);
        const double k4 = computeDerivative(H + dH, M + dH * k3, dir);

        return M + (dH / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    }

    [[nodiscard]] std::vector<HysteresisPoint> generateLoop(double H_max, std::size_t steps) const {
        std::vector<HysteresisPoint> points;
        points.reserve(steps * 4);

        double H = 0.0;
        double M = 0.0;
        constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;

        // Попередній вихід на насичення
        const double dH_init = H_max / static_cast<double>(steps);
        for (std::size_t i = 0; i < steps; ++i) {
            M = rk4Step(H, M, dH_init);
            H += dH_init;
        }

        // Основний замкнений цикл: +Hmax -> -Hmax -> +Hmax
        const double dH_down = -2.0 * H_max / static_cast<double>(steps * 2);
        for (std::size_t i = 0; i < steps * 2; ++i) {
            M = rk4Step(H, M, dH_down);
            H += dH_down;
            points.push_back({.H_field = H, .M_magnetization = M, .B_induction = mu0 * (H + M)});
        }

        const double dH_up = 2.0 * H_max / static_cast<double>(steps * 2);
        for (std::size_t i = 0; i < steps * 2; ++i) {
            M = rk4Step(H, M, dH_up);
            H += dH_up;
            points.push_back({.H_field = H, .M_magnetization = M, .B_induction = mu0 * (H + M)});
        }

        return points;
    }

    [[nodiscard]] static double calculateLosses(std::span<const HysteresisPoint> loop) noexcept {
        double area = 0.0;
        for (std::size_t i = 1; i < loop.size(); ++i) {
            const double dB = loop[i].B_induction - loop[i - 1].B_induction;
            const double H_avg = 0.5 * (loop[i].H_field + loop[i - 1].H_field);
            area += H_avg * dB;
        }
        return std::abs(area);
    }

private:
    JilesAthertonParams p_;
};

} // namespace physics
