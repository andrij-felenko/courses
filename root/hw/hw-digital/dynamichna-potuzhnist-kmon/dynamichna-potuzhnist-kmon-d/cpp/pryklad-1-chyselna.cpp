#include <iostream>
#include <cmath>
#include <algorithm>
#include <numbers>

struct CmosInverterConfig {
    double vdd{1.0};           // Напруга живлення, В
    double vth_n{0.25};        // Поріг NMOS, В
    double vth_p{0.25};        // Поріг PMOS, В
    double beta_n{1.2e-3};     // Крутизна NMOS, А/В^2
    double beta_p{0.8e-3};     // Крутизна PMOS, А/В^2
    double c_load{15.0e-15};   // Навантажувальна ємність, Ф (15 фФ)
    double t_rise{50.0e-12};   // Тривалість наростання, с (50 пс)
};

struct DynamicPowerReport {
    double energy_cap_fj{0.0};   // Ємнісна енергія, фДж
    double energy_sc_fj{0.0};    // Наскрізна енергія, фДж
    double energy_total_fj{0.0}; // Повна енергія, фДж
    double peak_sc_ma{0.0};      // Піковий струм, мА
    double sc_fraction_pct{0.0}; // Відсоток наскрізних втрат
};

class CmosTransientSimulator {
public:
    explicit CmosTransientSimulator(CmosInverterConfig cfg) noexcept : cfg_{cfg} {}

    [[nodiscard]] DynamicPowerReport run_simulation(double dt = 1e-13, double t_end = 200e-12) const noexcept {
        double v_out = cfg_.vdd;
        double total_energy = 0.0;
        double sc_energy = 0.0;
        double max_sc = 0.0;

        for (double t = 0.0; t <= t_end; t += dt) {
            const double v_in = (t < cfg_.t_rise) ? (cfg_.vdd * (t / cfg_.t_rise)) : cfg_.vdd;

            const double i_n = evaluate_mos(v_in, v_out, cfg_.vth_n, cfg_.beta_n);
            const double i_p = evaluate_mos(cfg_.vdd - v_in, cfg_.vdd - v_out, cfg_.vth_p, cfg_.beta_p);

            const double i_sc = std::min(i_n, i_p);
            max_sc = std::max(max_sc, i_sc);

            const double i_net_discharge = i_n - i_p;
            v_out = std::clamp(v_out - (i_net_discharge / cfg_.c_load) * dt, 0.0, cfg_.vdd);

            total_energy += (cfg_.vdd * i_p) * dt;
            sc_energy += (cfg_.vdd * i_sc) * dt;
        }

        DynamicPowerReport rep{};
        rep.energy_total_fj = total_energy * 1e15;
        rep.energy_sc_fj = sc_energy * 1e15;
        rep.energy_cap_fj = (total_energy - sc_energy) * 1e15;
        rep.peak_sc_ma = max_sc * 1e3;
        rep.sc_fraction_pct = (total_energy > 0.0) ? (sc_energy / total_energy) * 100.0 : 0.0;
        return rep;
    }

private:
    [[nodiscard]] static constexpr double evaluate_mos(double vgs, double vds, double vth, double beta) noexcept {
        if (vgs <= vth) return 0.0;
        const double vov = vgs - vth;
        return (vds < vov) ? beta * (vov * vds - 0.5 * vds * vds) : 0.5 * beta * vov * vov;
    }

    CmosInverterConfig cfg_;
};
