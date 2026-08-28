#include <iostream>
#include <array>
#include <cmath>
#include <vector>
#include <fstream>
#include <stdexcept>

// Фізичні фундаментальні константи у СІ
constexpr double HBAR = 1.054571817e-34;
constexpr double E_CHARGE = 1.602176634e-19;
constexpr double MU_0 = 4.0 * M_PI * 1e-7;
constexpr double GAMMA_0 = 2.211e5;

struct MacrospinState {
    std::array<double, 3> m; // Вектор намагніченості (mx, my, mz)
};

class STTCellModel {
public:
    double Ms = 1.0e6;         // А/м
    double Hk_eff = 3.0e5;     // А/м
    double alpha = 0.01;       // загасання
    double P = 0.65;           // поляризація
    double thickness = 1.4e-9; // м
    double diameter = 45e-9;   // м
    double R_P = 4500.0;       // Ом
    double TMR = 1.80;         // 180%

    [[nodiscard]] double get_area() const noexcept {
        return M_PI * (diameter * 0.5) * (diameter * 0.5);
    }

    [[nodiscard]] double get_critical_current_j0() const noexcept {
        const double g0 = P / (1.0 + P * P);
        return (2.0 * E_CHARGE * MU_0 * Ms * thickness * alpha * Hk_eff) / (HBAR * P * g0);
    }
};

class LLGSIntegratorRK4 {
private:
    STTCellModel cell_;
    double gamma_prime_;
    std::array<double, 3> p_vec_{0.0, 0.0, 1.0};

    static std::array<double, 3> cross(const std::array<double, 3>& a, const std::array<double, 3>& b) noexcept {
        return {
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        };
    }

    static double dot(const std::array<double, 3>& a, const std::array<double, 3>& b) noexcept {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    static std::array<double, 3> normalize(const std::array<double, 3>& v) {
        const double norm = std::sqrt(dot(v, v));
        if (norm < 1e-15) throw std::runtime_error("Zero norm vector in LLGS");
        return {v[0] / norm, v[1] / norm, v[2] / norm};
    }

public:
    explicit LLGSIntegratorRK4(STTCellModel cell)
        : cell_(cell), gamma_prime_(GAMMA_0 / (1.0 + cell.alpha * cell.alpha)) {}

    [[nodiscard]] std::array<double, 3> compute_rhs(const std::array<double, 3>& m, double J_e) const noexcept {
        const std::array<double, 3> H_eff = {0.0, 0.0, cell_.Hk_eff * m[2]};
        const double cos_theta = dot(m, p_vec_);
        const double g_theta = cell_.P / (1.0 + cell_.P * cell_.P * cos_theta);
        const double a_J = (HBAR * cell_.P * J_e * g_theta) / (2.0 * E_CHARGE * MU_0 * cell_.Ms * cell_.thickness);

        const auto m_cross_H = cross(m, H_eff);
        const auto m_cross_m_cross_H = cross(m, m_cross_H);
        const auto m_cross_p = cross(m, p_vec_);
        const auto m_cross_m_cross_p = cross(m, m_cross_p);

        std::array<double, 3> dm_dt;
        for (size_t i = 0; i < 3; ++i) {
            dm_dt[i] = - gamma_prime_ * m_cross_H[i]
                       - cell_.alpha * gamma_prime_ * m_cross_m_cross_H[i]
                       - gamma_prime_ * a_J * m_cross_m_cross_p[i]
                       + cell_.alpha * gamma_prime_ * a_J * m_cross_p[i];
        }
        return dm_dt;
    }

    [[nodiscard]] std::array<double, 3> step(const std::array<double, 3>& m, double dt, double J_e) const {
        const auto k1 = compute_rhs(m, J_e);
        
        std::array<double, 3> m_k2;
        for (size_t i = 0; i < 3; ++i) m_k2[i] = m[i] + 0.5 * dt * k1[i];
        const auto k2 = compute_rhs(m_k2, J_e);

        std::array<double, 3> m_k3;
        for (size_t i = 0; i < 3; ++i) m_k3[i] = m[i] + 0.5 * dt * k2[i];
        const auto k3 = compute_rhs(m_k3, J_e);

        std::array<double, 3> m_k4;
        for (size_t i = 0; i < 3; ++i) m_k4[i] = m[i] + dt * k3[i];
        const auto k4 = compute_rhs(m_k4, J_e);

        std::array<double, 3> m_next;
        for (size_t i = 0; i < 3; ++i) {
            m_next[i] = m[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
        return normalize(m_next);
    }
};

int main() {
    STTCellModel cell;
    LLGSIntegratorRK4 integrator(cell);

    const double I_c0 = cell.get_critical_current_j0() * cell.get_area();
    const double I_write = 1.6 * I_c0;
    const double J_write = I_write / cell.get_area();

    std::array<double, 3> m = {std::sin(0.05), 0.0, std::cos(0.05)};
    const double dt = 0.1e-12; // 0.1 пс
    const size_t steps = 30000; // 3.0 нс

    for (size_t step = 0; step < steps; ++step) {
        m = integrator.step(m, dt, J_write);
    }

    std::cout << "Final mz after 3 ns: " << m[2] << std::endl;
    return 0;
}
