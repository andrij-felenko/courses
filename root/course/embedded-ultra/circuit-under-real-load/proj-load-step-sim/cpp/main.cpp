#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <chrono>

namespace pdn {

struct Config {
    double v_source{3.30};        // ЕРС джерела живлення, В
    double r_source{0.05};        // Внутрішній опір джерела, Ом
    double r_wire{0.20};          // Активний опір провідників, Ом
    double l_wire{150e-9};        // Паразитна індуктивність кабелю, Гн
    
    double c_bulk{47e-6};         // Ємність об'ємного електроліту, Ф
    double esr_bulk{0.35};        // ESR електроліту, Ом
    
    double c_mlcc{10e-6};         // Локальна керамічна ємність, Ф
    double esr_mlcc{0.01};        // ESR кераміки, Ом
    
    double v_bor_threshold{2.70}; // Поріг детектора Brownout Reset, В
};

struct MotorLoad {
    double i_mcu_base{0.030};     // Струм спокою мікроконтролера, А
    double r_coil{1.50};          // Активний опір обмотки двигуна, Ом
    double i_run{0.250};          // Номінальний робочий струм, А
    double tau_mech{3e-3};        // Механічна стала часу розгону, с
    double t_start{1e-3};         // Час подачі сигналу пуску, с

    [[nodiscard]] double current_at(double t, double v_bus) const noexcept {
        double i_total = i_mcu_base;
        if (t >= t_start) {
            const double dt = t - t_start;
            const double i_stall = (v_bus > 0.1) ? (v_bus / r_coil) : 0.0;
            const double i_motor = i_run + (i_stall - i_run) * std::exp(-dt / tau_mech);
            i_total += i_motor;
        }
        return i_total;
    }
};

struct Result {
    double v_min{0.0};
    double t_v_min{0.0};
    double v_final{0.0};
    bool bor_triggered{false};
    double bor_duration{0.0};
};

class Simulator {
public:
    explicit Simulator(Config cfg, MotorLoad load)
        : cfg_{cfg}, load_{load} {}

    [[nodiscard]] Result run(double t_total, double dt) const {
        Result res{};
        res.v_min = cfg_.v_source;

        double i_wire = load_.i_mcu_base;
        double u_c_bulk = cfg_.v_source - i_wire * (cfg_.r_source + cfg_.r_wire);
        double u_c_mlcc = u_c_bulk;
        double v_bus = u_c_bulk;

        const double g_bulk = 1.0 / cfg_.esr_bulk;
        const double g_mlcc = 1.0 / cfg_.esr_mlcc;
        const double g_total = g_bulk + g_mlcc;

        const auto total_steps = static_cast<std::size_t>(t_total / dt);

        for (std::size_t step = 0; step < total_steps; ++step) {
            const double t = static_cast<double>(step) * dt;
            const double i_load = load_.current_at(t, v_bus);

            v_bus = (i_wire - i_load + g_bulk * u_c_bulk + g_mlcc * u_c_mlcc) / g_total;

            const double i_c_bulk = (v_bus - u_c_bulk) * g_bulk;
            const double i_c_mlcc = (v_bus - u_c_mlcc) * g_mlcc;

            const double di_wire = (cfg_.v_source - i_wire * (cfg_.r_source + cfg_.r_wire) - v_bus) / cfg_.l_wire;
            const double du_bulk = i_c_bulk / cfg_.c_bulk;
            const double du_mlcc = i_c_mlcc / cfg_.c_mlcc;

            i_wire += di_wire * dt;
            u_c_bulk += du_bulk * dt;
            u_c_mlcc += du_mlcc * dt;

            if (v_bus < res.v_min) {
                res.v_min = v_bus;
                res.t_v_min = t;
            }

            if (v_bus < cfg_.v_bor_threshold) {
                res.bor_triggered = true;
                res.bor_duration += dt;
            }
        }

        res.v_final = v_bus;
        return res;
    }

private:
    Config cfg_;
    MotorLoad load_;
};

} // namespace pdn

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++ Чисельне моделювання PDN під динамічним навантаженням ===\n\n";

    pdn::Config cfg{};
    pdn::MotorLoad load{};

    pdn::Simulator sim1{cfg, load};
    const auto r1 = sim1.run(10e-3, 10e-9);

    std::cout << "[Сценарій 1: C_bulk = 47 мкФ]\n";
    std::cout << "  Мінімальна напруга V_min: " << r1.v_min << " В (на " << r1.t_v_min * 1000.0 << " мс)\n";
    std::cout << "  Усталена напруга V_final: " << r1.v_final << " В\n";
    std::cout << "  Спрацювання BOR: " << (r1.bor_triggered ? "ТАК (аварійний ресет)" : "НІ")
              << " | Тривалість провалу: " << r1.bor_duration * 1e6 << " мкс\n\n";

    // Посилення ємності для усунення Brownout Reset
    cfg.c_bulk = 220e-6;
    cfg.esr_bulk = 0.08;

    pdn::Simulator sim2{cfg, load};
    const auto r2 = sim2.run(10e-3, 10e-9);

    std::cout << "[Сценарій 2: C_bulk = 220 мкФ з низьким ESR]\n";
    std::cout << "  Мінімальна напруга V_min: " << r2.v_min << " В (на " << r2.t_v_min * 1000.0 << " мс)\n";
    std::cout << "  Усталена напруга V_final: " << r2.v_final << " В\n";
    std::cout << "  Спрацювання BOR: " << (r2.bor_triggered ? "ТАК" : "НІ (живлення стабільне)") << "\n";

    return 0;
}
