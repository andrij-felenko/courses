#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <iomanip>

class PMTJSimulator {
private:
    static constexpr double hbar = 1.0545718e-34;
    static constexpr double e_charge = 1.6021766e-19;
    static constexpr double gamma0 = 2.211e5;
    static constexpr double mu0 = 1.256637e-6;

    double ms;
    double hk_eff;
    double alpha;
    double polarization;
    double t_fl;

    std::array<double, 3> cross(const std::array<double, 3>& a, const std::array<double, 3>& b) const {
        return {
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        };
    }

public:
    PMTJSimulator(double ms_val = 1.0e6, double hk_val = 0.3, double alpha_val = 0.01,
                  double pol_val = 0.6, double t_fl_nm = 1.3)
        : ms(ms_val), hk_eff(hk_val), alpha(alpha_val), polarization(pol_val), t_fl(t_fl_nm * 1.0e-9) {}

    double compute_stt_amplitude(double j_density) const {
        return (hbar * j_density * polarization) / (2.0 * e_charge * ms * t_fl);
    }

    std::array<double, 3> compute_dmdt(const std::array<double, 3>& m, double j_density) const {
        double a_j = compute_stt_amplitude(j_density);
        std::array<double, 3> h_eff = {0.0, 0.0, (hk_eff / mu0) * m[2]};
        std::array<double, 3> m_p = {0.0, 0.0, 1.0};

        auto m_x_h = cross(m, h_eff);
        auto m_x_m_x_h = cross(m, m_x_h);
        auto m_x_mp = cross(m, m_p);
        auto m_x_m_x_mp = cross(m, m_x_mp);

        double factor = -gamma0 / (1.0 + alpha * alpha);
        std::array<double, 3> dm;
        for (size_t i = 0; i < 3; ++i) {
            dm[i] = factor * (m_x_h[i] + alpha * m_x_m_x_h[i] - a_j * m_x_m_x_mp[i] - alpha * a_j * m_x_mp[i]);
        }
        return dm;
    }

    std::vector<double> simulate_pulse(double j_density, double pulse_duration_ns, double dt_ps = 0.1) {
        double dt = dt_ps * 1.0e-12;
        size_t steps = static_cast<size_t>((pulse_duration_ns * 1.0e-9) / dt);

        double theta_init = 3.0 * (M_PI / 180.0);
        std::array<double, 3> m = {std::sin(theta_init), 0.0, -std::cos(theta_init)};
        std::vector<double> history_mz;
        history_mz.reserve(steps);

        for (size_t s = 0; s < steps; ++s) {
            history_mz.push_back(m[2]);

            auto k1 = compute_dmdt(m, j_density);

            std::array<double, 3> m_k2;
            for (size_t i = 0; i < 3; ++i) m_k2[i] = m[i] + 0.5 * dt * k1[i];
            auto k2 = compute_dmdt(m_k2, j_density);

            std::array<double, 3> m_k3;
            for (size_t i = 0; i < 3; ++i) m_k3[i] = m[i] + 0.5 * dt * k2[i];
            auto k3 = compute_dmdt(m_k3, j_density);

            std::array<double, 3> m_k4;
            for (size_t i = 0; i < 3; ++i) m_k4[i] = m[i] + dt * k3[i];
            auto k4 = compute_dmdt(m_k4, j_density);

            std::array<double, 3> m_next;
            for (size_t i = 0; i < 3; ++i) {
                m_next[i] = m[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
            }

            double norm = std::sqrt(m_next[0] * m_next[0] + m_next[1] * m_next[1] + m_next[2] * m_next[2]);
            for (size_t i = 0; i < 3; ++i) m[i] = m_next[i] / norm;
        }

        return history_mz;
    }
};

int main() {
    PMTJSimulator sim;
    double j_test = 7.5e10; // 7.5 MA/cm²
    auto history = sim.simulate_pulse(j_test, 3.0);
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Кінцеве m_z після 3 нс імпульсу: " << history.back() << std::endl;
    if (history.back() > 0.5) {
        std::cout << "УСПІХ: Намагніченість переключилася в паралельний стан (P)!" << std::endl;
    } else {
        std::cout << "ПОМИЛКА: Переключення не відбулося." << std::endl;
    }
    return 0;
}
