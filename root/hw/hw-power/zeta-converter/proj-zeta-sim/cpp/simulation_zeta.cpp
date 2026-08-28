// simulation_zeta.cpp — Об'єктно-орієнтована числова симуляція Zeta-перетворювача
#include <iostream>
#include <iomanip>
#include <cmath>
#include <array>
#include <vector>
#include <span>

namespace power_sim {

struct ZetaConfig {
    double vin{12.0};        // Вхідна напруга, В
    double r_load{6.0};      // Опір навантаження, Ом
    double f_sw{250000.0};   // Частота перемикання, Гц
    double duty{0.512};      // Шпаруватість [0..1]
    double l1{27e-6};        // Вхідна індуктивність, Гн
    double l2{33e-6};        // Вихідна індуктивність, Гн
    double k_coupling{0.90}; // Коефіцієнт зв'язку осердя
    double c_c{14.1e-6};     // Розділовий конденсатор, Ф
    double c_out{91e-6};     // Вихідна ємність, Ф
    double r_on{0.015};      // Опір відкритого ключа, Ом
    double v_diode{0.45};    // Падіння на діоді Шотткі, В
};

struct SystemState {
    double i_l1{0.0};        // Струм індуктивності L1, А
    double i_l2{0.0};        // Струм індуктивності L2, А
    double v_cc{0.0};        // Напруга на ємності Cc, В
    double v_out{0.0};       // Вихідна напруга Vвих, В
};

class ZetaSimulator {
public:
    explicit ZetaSimulator(ZetaConfig cfg) : cfg_(cfg) {
        double m = cfg_.k_coupling * std::sqrt(cfg_.l1 * cfg_.l2);
        det_l_ = cfg_.l1 * cfg_.l2 - m * m;
        mutual_l_ = m;
    }

    [[nodiscard]] SystemState step(const SystemState& current, double time, double dt) const {
        auto k1 = compute_derivatives(current, time);
        auto k2 = compute_derivatives(advance_state(current, k1, 0.5 * dt), time + 0.5 * dt);
        auto k3 = compute_derivatives(advance_state(current, k2, 0.5 * dt), time + 0.5 * dt);
        auto k4 = compute_derivatives(advance_state(current, k3, dt), time + dt);

        SystemState next;
        next.i_l1 = current.i_l1 + (dt / 6.0) * (k1.i_l1 + 2.0 * k2.i_l1 + 2.0 * k3.i_l1 + k4.i_l1);
        next.i_l2 = current.i_l2 + (dt / 6.0) * (k1.i_l2 + 2.0 * k2.i_l2 + 2.0 * k3.i_l2 + k4.i_l2);
        next.v_cc = current.v_cc + (dt / 6.0) * (k1.v_cc + 2.0 * k2.v_cc + 2.0 * k3.v_cc + k4.v_cc);
        next.v_out = current.v_out + (dt / 6.0) * (k1.v_out + 2.0 * k2.v_out + 2.0 * k3.v_out + k4.v_out);
        return next;
    }

private:
    [[nodiscard]] SystemState compute_derivatives(const SystemState& s, double t) const {
        double period = 1.0 / cfg_.f_sw;
        double phase = std::fmod(t, period);
        bool switch_on = (phase < cfg_.duty * period);

        double v_sw1, v_sw2;
        double i_cc_flow;

        if (switch_on) {
            v_sw1 = cfg_.vin - (s.i_l1 + s.i_l2) * cfg_.r_on;
            v_sw2 = v_sw1 + s.v_cc;
            i_cc_flow = -s.i_l2;
        } else {
            v_sw2 = -cfg_.v_diode;
            v_sw1 = v_sw2 - s.v_cc;
            i_cc_flow = s.i_l1;
        }

        double v_l1_app = v_sw1;
        double v_l2_app = v_sw2 - s.v_out;

        SystemState deriv;
        deriv.i_l1 = (cfg_.l2 * v_l1_app - mutual_l_ * v_l2_app) / det_l_;
        deriv.i_l2 = (cfg_.l1 * v_l2_app - mutual_l_ * v_l1_app) / det_l_;
        deriv.v_cc = i_cc_flow / cfg_.c_c;
        deriv.v_out = (s.i_l2 - s.v_out / cfg_.r_load) / cfg_.c_out;
        return deriv;
    }

    [[nodiscard]] static SystemState advance_state(const SystemState& s, const SystemState& d, double factor) {
        return {
            s.i_l1 + d.i_l1 * factor,
            s.i_l2 + d.i_l2 * factor,
            s.v_cc + d.v_cc * factor,
            s.v_out + d.v_out * factor
        };
    }

    ZetaConfig cfg_;
    double det_l_{0.0};
    double mutual_l_{0.0};
};

} // namespace power_sim

int main() {
    using namespace power_sim;

    ZetaConfig cfg;
    ZetaSimulator sim(cfg);
    SystemState state;

    constexpr double dt = 2.0e-8;  // 20 нс крок
    constexpr double t_end = 0.004; // 4 мс

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "# Час (мс)    I_L1 (A)    I_L2 (A)    V_Cc (V)    V_out (V)\n";

    int step = 0;
    for (double t = 0.0; t < t_end; t += dt, ++step) {
        state = sim.step(state, t, dt);

        if (step % 2500 == 0) {
            std::cout << std::setw(8) << (t * 1000.0) << "    "
                      << std::setw(8) << state.i_l1 << "    "
                      << std::setw(8) << state.i_l2 << "    "
                      << std::setw(8) << state.v_cc << "    "
                      << std::setw(8) << state.v_out << "\n";
        }
    }

    std::cout << "\n# Результати симуляції в усталеному режимі:\n";
    std::cout << "Вихідна напруга V_out = " << state.v_out << " В\n";
    std::cout << "Напруга на Cc   V_Cc  = " << state.v_cc << " В (V_Cc == V_out)\n";
    std::cout << "Вхідний струм   I_L1  = " << state.i_l1 << " А\n";
    std::cout << "Вихідний струм  I_L2  = " << state.i_l2 << " А\n";

    return 0;
}
