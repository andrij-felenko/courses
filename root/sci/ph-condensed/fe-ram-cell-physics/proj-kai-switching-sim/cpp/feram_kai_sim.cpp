// feram_kai_sim.cpp - Об'єктно-орієнтований симулятор FeRAM комірки (C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <memory>
#include <span>

struct FeRamConfig {
    double area_cap_um2{0.25};
    double p_remnant_uc{22.0};
    double c_lin_ff{5.0};
    double c_bitline_ff{60.0};
    double tau_0_ns{2.5};
    double avrami_n{2.2};
    double v_dd_volts{1.8};
    double t_rise_ns{1.0};
};

struct SimulationFrame {
    double time_ns{0.0};
    double v_pl_volts{0.0};
    double i_sw_ma{0.0};
    double i_lin_ma{0.0};
    double v_bl_state1_volts{0.0};
    double v_bl_state0_volts{0.0};

    [[nodiscard]] double sense_margin_mv() const noexcept {
        return (v_bl_state1_volts - v_bl_state0_volts) * 1000.0;
    }
};

class FeRamSimulator {
public:
    explicit FeRamSimulator(FeRamConfig config) : config_(config) {}

    [[nodiscard]] std::vector<SimulationFrame> run(double total_time_ns, double dt_ns) const {
        const size_t steps = static_cast<size_t>(total_time_ns / dt_ns) + 1;
        std::vector<SimulationFrame> timeline;
        timeline.reserve(steps);

        const double area_cm2 = config_.area_cap_um2 * 1.0e-8;
        const double pr_c_cm2 = config_.p_remnant_uc * 1.0e-6;
        const double q_sw_total_c = 2.0 * pr_c_cm2 * area_cm2;
        
        const double c_lin_farads = config_.c_lin_ff * 1.0e-15;
        const double c_bl_farads = config_.c_bitline_ff * 1.0e-15;
        const double c_total_farads = c_lin_farads + c_bl_farads;

        double v_bl_1 = 0.0;
        double v_bl_0 = 0.0;

        for (size_t i = 0; i < steps; ++i) {
            const double t = i * dt_ns;
            
            double v_pl = 0.0;
            double dv_pl_dt = 0.0;
            if (t < config_.t_rise_ns) {
                v_pl = config_.v_dd_volts * (t / config_.t_rise_ns);
                dv_pl_dt = config_.v_dd_volts / config_.t_rise_ns;
            } else {
                v_pl = config_.v_dd_volts;
                dv_pl_dt = 0.0;
            }

            const double dmu_dt = compute_dmu_dt(t);
            const double i_sw_amp = q_sw_total_c * (dmu_dt * 1.0e9);
            const double i_lin_amp = c_lin_farads * (dv_pl_dt * 1.0e9);

            const double dv_bl_1 = ((i_sw_amp + i_lin_amp) / c_total_farads) * (dt_ns * 1.0e-9);
            const double dv_bl_0 = (i_lin_amp / c_total_farads) * (dt_ns * 1.0e-9);

            v_bl_1 += dv_bl_1;
            v_bl_0 += dv_bl_0;

            timeline.push_back(SimulationFrame{
                .time_ns = t,
                .v_pl_volts = v_pl,
                .i_sw_ma = i_sw_amp * 1.0e3,
                .i_lin_ma = i_lin_amp * 1.0e3,
                .v_bl_state1_volts = v_bl_1,
                .v_bl_state0_volts = v_bl_0
            });
        }

        return timeline;
    }

private:
    FeRamConfig config_;

    [[nodiscard]] double compute_dmu_dt(double t_ns) const noexcept {
        if (t_ns <= 0.0 || config_.tau_0_ns <= 0.0) {
            return 0.0;
        }
        const double norm_t = t_ns / config_.tau_0_ns;
        const double term1 = (config_.avrami_n / config_.tau_0_ns) * std::pow(norm_t, config_.avrami_n - 1.0);
        const double term2 = std::exp(-std::pow(norm_t, config_.avrami_n));
        return term1 * term2;
    }
};

void print_summary(std::span<const SimulationFrame> results) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Time(ns) | V_PL(V) | I_sw(mA) | V_BL[1](V) | V_BL[0](V) | Sense_Margin(mV)\n";
    std::cout << "-------------------------------------------------------------------------\n";

    for (size_t i = 0; i < results.size(); i += 20) {
        const auto& frame = results[i];
        std::cout << std::setw(8) << frame.time_ns << " | "
                  << std::setw(7) << frame.v_pl_volts << " | "
                  << std::setw(8) << frame.i_sw_ma << " | "
                  << std::setw(10) << frame.v_bl_state1_volts << " | "
                  << std::setw(10) << frame.v_bl_state0_volts << " | "
                  << std::setw(17) << std::setprecision(1) << frame.sense_margin_mv() << "\n"
                  << std::setprecision(2);
    }
}

int main() {
    const FeRamConfig config{
        .area_cap_um2 = 0.25,
        .p_remnant_uc = 22.0,
        .c_lin_ff = 5.0,
        .c_bitline_ff = 60.0,
        .tau_0_ns = 2.5,
        .avrami_n = 2.2,
        .v_dd_volts = 1.8,
        .t_rise_ns = 1.0
    };

    FeRamSimulator simulator(config);
    auto results = simulator.run(10.0, 0.05);

    print_summary(results);

    return 0;
}
