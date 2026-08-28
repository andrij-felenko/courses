#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <expected>
#include <string>

namespace pdn {

struct Scenario {
    double v_bat_ocv{3.00};        // Напруга холостого ходу джерела, В
    double r_src{30.0};            // Внутрішній опір джерела живлення, Ом
    double i_peak{0.280};          // Піковий струм імпульсу навантаження, А
    double t_pulse{0.020};         // Тривалість імпульсу, с
    double t_rise{0.0001};         // Час наростання фронту струму, с
    double v_bor_limit{2.20};      // Поріг спрацьовування Brownout Reset, В
    double v_safety_margin{0.20};  // Інженерний запас надійності, В
};

struct Capacitor {
    double c_nominal{100e-6};      // Номінальна ємність, Ф
    double r_esr{0.040};           // Еквівалентний послідовний опір ESR, Ом
    double dc_bias_factor{0.15};   // Деградація ємності під DC Bias (0.0..1.0)
};

struct SimulationResult {
    double v_min{0.0};
    double t_v_min{0.0};
    bool is_bor_triggered{false};
};

class Simulator {
public:
    static double calc_effective_capacitance(const Capacitor& cap, double v_now) noexcept {
        const double derating = std::clamp(1.0 - (cap.dc_bias_factor * (v_now / 3.3)), 0.20, 1.0);
        return cap.c_nominal * derating;
    }

    static double get_load_current(const Scenario& sc, double t) noexcept {
        constexpr double i_sleep = 5e-6; // Струм режиму сну: 5 мкА
        if (t < 0.0 || t > sc.t_pulse) {
            return i_sleep;
        }
        if (t < sc.t_rise && sc.t_rise > 0.0) {
            return i_sleep + (sc.i_peak - i_sleep) * (t / sc.t_rise);
        }
        return sc.i_peak;
    }

    static SimulationResult run(const Scenario& sc, const Capacitor& cap) noexcept {
        SimulationResult res{ sc.v_bat_ocv, 0.0, false };
        constexpr double dt = 1e-6; // Крок інтегрування: 1 мкс
        const double t_end = sc.t_pulse * 1.5;

        double v_c = sc.v_bat_ocv;
        double v_bus = sc.v_bat_ocv;

        for (double t = 0.0; t <= t_end; t += dt) {
            const double i_load = get_load_current(sc, t);

            // Розподіл струмів за законами Кірхгофа
            double i_src = (sc.v_bat_ocv - v_c + i_load * cap.r_esr) / (sc.r_src + cap.r_esr);
            if (i_src < 0.0) i_src = 0.0;

            const double i_cap = i_load - i_src;
            v_bus = v_c - (i_cap * cap.r_esr);

            const double c_eff = calc_effective_capacitance(cap, v_c);
            v_c -= (i_cap / c_eff) * dt;

            if (v_bus < res.v_min) {
                res.v_min = v_bus;
                res.t_v_min = t;
            }

            if (v_bus < sc.v_bor_limit) {
                res.is_bor_triggered = true;
            }
        }

        return res;
    }

    static std::expected<double, std::string> find_min_capacitance(
        const Scenario& sc, double r_esr, double dc_bias) noexcept
    {
        double c_low = 1e-6;
        double c_high = 20000e-6;
        const double target_min_v = sc.v_bor_limit + sc.v_safety_margin;

        Capacitor test_cap{ c_high, r_esr, dc_bias };
        const auto check_max = run(sc, test_cap);
        if (check_max.v_min < target_min_v) {
            return std::unexpected("Завеликий ESR буфера або джерела: просідання не компенсується");
        }

        for (int iter = 0; iter < 40; ++iter) {
            const double c_mid = (c_low + c_high) * 0.5;
            test_cap.c_nominal = c_mid;
            const auto r = run(sc, test_cap);

            if (r.v_min >= target_min_v && !r.is_bor_triggered) {
                c_high = c_mid;
            } else {
                c_low = c_mid;
            }
        }

        return c_high;
    }
};

} // namespace pdn

int main() {
    const pdn::Scenario sc{
        .v_bat_ocv = 3.00,
        .r_src = 30.0,
        .i_peak = 0.280,
        .t_pulse = 0.020,
        .t_rise = 0.0001,
        .v_bor_limit = 2.20,
        .v_safety_margin = 0.20
    };

    constexpr double r_esr = 0.040;
    constexpr double dc_bias = 0.15;

    const auto min_cap_res = pdn::Simulator::find_min_capacitance(sc, r_esr, dc_bias);

    if (min_cap_res.has_value()) {
        const double c_opt = min_cap_res.value();
        std::cout << "Мінімальна ємність буфера (C++): "
                  << (c_opt * 1e6) << " мкФ (" << (c_opt * 1e3) << " мФ)\n";

        const pdn::Capacitor final_cap{ c_opt, r_esr, dc_bias };
        const auto sim = pdn::Simulator::run(sc, final_cap);
        std::cout << "Мінімум напруги шини: " << sim.v_min << " В при t = "
                  << (sim.t_v_min * 1000.0) << " мс\n";
        std::cout << "Захист BOR: "
                  << (sim.is_bor_triggered ? "ЗБІЙ" : "В НОРМІ") << "\n";
    } else {
        std::cerr << "Помилка розрахунку: " << min_cap_res.error() << "\n";
    }

    return 0;
}
