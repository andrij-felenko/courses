#include <iostream>
#include <cmath>
#include <vector>
#include <iomanip>
#include <algorithm>

namespace pv_sim {

constexpr double K_B = 1.380649e-23;
constexpr double Q_E = 1.60217663e-19;

struct SolarCellParameters {
    double temp_k{298.15};     // Температура елемента (K)
    double area_cm2{244.3};    // Площа елемента (см²)
    double i_ph{10.2};         // Фотострум (А)
    double i_0{1e-11};         // Зворотний струм насичення диода (А)
    double n_ideality{1.1};    // Фактор ідеальності диода
    double r_s{0.005};         // Послідовний опір (Ом)
    double r_sh{500.0};        // Паралельний опір (Ом)
    double p_in_wm2{1000.0};    // Оптична потужність AM1.5G (Вт/м²)
};

struct SolarCellResults {
    double v_oc{0.0};
    double i_sc{0.0};
    double v_mp{0.0};
    double i_mp{0.0};
    double p_max{0.0};
    double fill_factor{0.0};
    double efficiency{0.0};
};

class SolarCellSimulator {
public:
    explicit SolarCellSimulator(SolarCellParameters params)
        : params_(std::move(params)) {}

    [[nodiscard]] double solveCurrent(double v) const {
        const double v_t = (params_.n_ideality * K_B * params_.temp_k) / Q_E;
        double i_curr = params_.i_ph;

        for (int iter = 0; iter < 100; ++iter) {
            double arg = (v + i_curr * params_.r_s) / v_t;
            if (arg > 80.0) arg = 80.0;

            const double exp_val = std::exp(arg);
            const double f = params_.i_ph - params_.i_0 * (exp_val - 1.0) 
                             - (v + i_curr * params_.r_s) / params_.r_sh - i_curr;
            const double df = -params_.i_0 * (params_.r_s / v_t) * exp_val 
                              - params_.r_s / params_.r_sh - 1.0;

            const double i_next = i_curr - f / df;
            if (std::abs(i_next - i_curr) < 1e-9) {
                return std::max(0.0, i_next);
            }
            i_curr = i_next;
        }
        return std::max(0.0, i_curr);
    }

    [[nodiscard]] SolarCellResults analyze() const {
        SolarCellResults res{};
        res.i_sc = solveCurrent(0.0);

        // Пошук V_oc бісекцією
        double v_low = 0.0, v_high = 1.2;
        for (int i = 0; i < 50; ++i) {
            const double v_mid = 0.5 * (v_low + v_high);
            if (solveCurrent(v_mid) > 1e-7) {
                v_low = v_mid;
            } else {
                v_high = v_mid;
            }
        }
        res.v_oc = 0.5 * (v_low + v_high);

        // Сканування IV характеристичного профілю
        constexpr int STEPS = 1000;
        const double dv = res.v_oc / STEPS;

        for (int k = 0; k <= STEPS; ++k) {
            const double v = k * dv;
            const double i = solveCurrent(v);
            const double p_val = v * i;

            if (p_val > res.p_max) {
                res.p_max = p_val;
                res.v_mp = v;
                res.i_mp = i;
            }
        }

        if (res.v_oc * res.i_sc > 0.0) {
            res.fill_factor = res.p_max / (res.v_oc * res.i_sc);
        }

        const double p_in_watts = params_.p_in_wm2 * (params_.area_cm2 / 10000.0);
        if (p_in_watts > 0.0) {
            res.efficiency = res.p_max / p_in_watts;
        }

        return res;
    }

private:
    SolarCellParameters params_;
};

} // namespace pv_sim

int main() {
    pv_sim::SolarCellParameters cell_params{};
    pv_sim::SolarCellSimulator simulator(cell_params);
    const auto r = simulator.analyze();

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Симуляція сонячного елемента (C++17) ===\n";
    std::cout << "Струм к.з. (I_sc):            " << r.i_sc << " А\n";
    std::cout << "Напруга х.х. (V_oc):           " << r.v_oc << " В\n";
    std::cout << "Напруга в точці MPP (V_mp):    " << r.v_mp << " В\n";
    std::cout << "Струм в точці MPP (I_mp):      " << r.i_mp << " А\n";
    std::cout << "Максимальна потужність (Pmax): " << r.p_max << " Вт\n";
    std::cout << std::setprecision(2);
    std::cout << "Фактор заповнення (FF):        " << r.fill_factor * 100.0 << " %\n";
    std::cout << "Розрахунковий ККД (η):         " << r.efficiency * 100.0 << " %\n";

    return 0;
}
