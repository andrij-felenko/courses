#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>

class OxRamSimulator {
private:
    struct Params {
        double x_gap = 1.2e-9;        // Товщина зазору (м)
        double R_on = 1000.0;         // Опір у стані LRS (Ом)
        double E_a = 0.85 * 1.602e-19;// Енергія активації (Дж)
        double a_lattice = 0.3e-9;   // Постійна ґратки (м)
        double I_comp = 1e-4;         // Струм обмеження (А)
    } p_;

    static constexpr double q = 1.602e-19;
    static constexpr double kB = 1.38e-23;
    static constexpr double L_W = 2.44e-8;
    static constexpr double T0 = 300.0;
    static constexpr double v0 = 1e4;

public:
    struct State {
        double voltage;
        double current;
        double gap;
    };

    explicit OxRamSimulator(double initial_gap = 1.2e-9, double i_comp = 1e-4) {
        p_.x_gap = initial_gap;
        p_.I_comp = i_comp;
    }

    State step(double V_app, double dt) {
        const double R_gap = p_.R_on * std::exp(10.25e9 * p_.x_gap);
        const double R_total = p_.R_on + R_gap;

        double I_cell = V_app / R_total;
        if (std::abs(I_cell) > p_.I_comp) {
            I_cell = std::copysign(p_.I_comp, I_cell);
        }

        const double V_gap = I_cell * R_gap;
        const double E_gap = std::abs(V_gap) / std::max(p_.x_gap, 1e-10);

        const double T_max = std::sqrt(T0 * T0 + (V_gap * V_gap) / (4.0 * L_W));

        double arg = (q * p_.a_lattice * E_gap) / (2.0 * kB * T_max);
        arg = std::min(arg, 50.0);

        const double v_drift = 2.0 * p_.a_lattice * v0 * std::exp(-p_.E_a / (kB * T_max)) * std::sinh(arg);
        const double dx_dt = (V_app > 0) ? -v_drift : v_drift * 0.1;

        p_.x_gap = std::clamp(p_.x_gap + dx_dt * dt, 0.0, 2.0e-9);

        return { V_app, I_cell, p_.x_gap };
    }

    std::vector<State> run_ramp(double v_max, std::size_t steps, double dt) {
        std::vector<State> results;
        results.reserve(steps);

        for (std::size_t i = 0; i < steps; ++i) {
            double v = (static_cast<double>(i) / steps) * v_max;
            results.push_back(step(v, dt));
        }
        return results;
    }
};

int main() {
    OxRamSimulator sim(1.2e-9, 1e-4);
    auto trajectory = sim.run_ramp(2.0, 20, 1e-6);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Крок | Напруга (В) | Струм (мкА) | Зазор x_gap (нм)\n";
    std::cout << "--------------------------------------------------\n";

    std::size_t step_idx = 0;
    for (const auto& st : trajectory) {
        std::cout << std::setw(4) << step_idx++ << " | "
                  << std::setw(11) << st.voltage << " | "
                  << std::setw(11) << st.current * 1e6 << " | "
                  << std::setw(16) << st.gap * 1e9 << "\n";
    }
    return 0;
}
