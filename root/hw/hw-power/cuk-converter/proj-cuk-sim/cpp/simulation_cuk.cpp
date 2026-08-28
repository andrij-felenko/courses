// simulation_cuk.cpp — Об'єктно-орієнтована числова симуляція перетворювача Cuk
#include <iostream>
#include <iomanip>
#include <cmath>
#include <array>
#include <vector>
#include <span>

namespace power_sim {

struct ConverterConfig {
    double vin{24.0};        // Вхідна напруга, В
    double r_load{10.0};     // Опір навантаження, Ом
    double f_sw{200000.0};   // Частота перемикання, Гц
    double duty{0.3846};     // Шпаруватість [0..1]
    double l1{220e-6};       // Вхідна індуктивність, Гн
    double l2{150e-6};       // Вихідна індуктивність, Гн
    double k_coupling{0.88}; // Магнітний зв'язок обмоток
    double c1{9.4e-6};       // Ємнісний міст, Ф
    double c_out{91e-6};     // Вихідна ємність, Ф
    double r_on{0.020};      // Опір відкритого ключа, Ом
    double v_diode{0.45};    // Пряме падіння діода Шотткі, В
};

struct SystemState {
    double i_l1{0.0};        // Струм дроселя L1, А
    double i_l2{0.0};        // Струм дроселя L2, А
    double v_c1{0.0};        // Напруга на ємності C1, В
    double v_cout{0.0};      // Напруга на вихідній ємності, В
};

class CukSimulator {
public:
    explicit CukSimulator(ConverterConfig cfg) : cfg_(cfg) {
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
        next.v_c1 = current.v_c1 + (dt / 6.0) * (k1.v_c1 + 2.0 * k2.v_c1 + 2.0 * k3.v_c1 + k4.v_c1);
        next.v_cout = current.v_cout + (dt / 6.0) * (k1.v_cout + 2.0 * k2.v_cout + 2.0 * k3.v_cout + k4.v_cout);
        return next;
    }

private:
    [[nodiscard]] SystemState compute_derivatives(const SystemState& s, double t) const {
        double period = 1.0 / cfg_.f_sw;
        double phase = std::fmod(t, period);
        bool switch_on = (phase < cfg_.duty * period);

        double v_l1_app = switch_on ? (cfg_.vin - s.i_l1 * cfg_.r_on) 
                                    : (cfg_.vin - s.v_c1 + cfg_.v_diode);
        double v_l2_app = switch_on ? (-s.v_c1 + s.v_cout) 
                                    : (s.v_cout - cfg_.v_diode);
        double i_c1_flow = switch_on ? (-s.i_l2) : (s.i_l1);

        SystemState deriv;
        deriv.i_l1 = (cfg_.l2 * v_l1_app - mutual_l_ * v_l2_app) / det_l_;
        deriv.i_l2 = (cfg_.l1 * v_l2_app - mutual_l_ * v_l1_app) / det_l_;
        deriv.v_c1 = i_c1_flow / cfg_.c1;
        deriv.v_cout = (s.i_l2 - s.v_cout / cfg_.r_load) / cfg_.c_out;
        return deriv;
    }

    [[nodiscard]] static SystemState advance_state(const SystemState& s, const SystemState& d, double factor) {
        return {
            s.i_l1 + d.i_l1 * factor,
            s.i_l2 + d.i_l2 * factor,
            s.v_c1 + d.v_c1 * factor,
            s.v_cout + d.v_cout * factor
        };
    }

    ConverterConfig cfg_;
    double det_l_{0.0};
    double mutual_l_{0.0};
};

} // namespace power_sim

int main() {
    using namespace power_sim;

    ConverterConfig cfg;
    CukSimulator sim(cfg);
    SystemState current_state;

    constexpr double dt = 2.5e-8; // 25 нс крок
    constexpr double t_end = 0.005; // 5 мс

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "# Час (мс)    I_L1 (A)    I_L2 (A)    V_C1 (V)    V_out (V)\n";

    int step = 0;
    for (double t = 0.0; t < t_end; t += dt, ++step) {
        current_state = sim.step(current_state, t, dt);

        if (step % 2000 == 0) {
            std::cout << std::setw(8) << (t * 1000.0) << "    "
                      << std::setw(8) << current_state.i_l1 << "    "
                      << std::setw(8) << current_state.i_l2 << "    "
                      << std::setw(8) << current_state.v_c1 << "    "
                      << std::setw(8) << -current_state.v_cout << "\n";
        }
    }

    std::cout << "\n# Результати усталеного стану:\n";
    std::cout << "Вихідна напруга V_out = " << -current_state.v_cout << " В\n";
    std::cout << "Середня напруга V_C1  = " << current_state.v_c1 << " В\n";
    std::cout << "Вхідний струм   I_in  = " << current_state.i_l1 << " А\n";

    return 0;
}
