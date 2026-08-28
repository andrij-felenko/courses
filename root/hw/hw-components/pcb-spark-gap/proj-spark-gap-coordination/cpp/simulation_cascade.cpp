// simulation_cascade.cpp — чисельне моделювання каскаду захисту Spark Gap + TVS (C++20)
#include <iostream>
#include <iomanip>
#include <vector>
#include <string_view>
#include <cmath>
#include <numbers>

enum class GapState {
    Waiting,
    Forming,
    ArcIgnited
};

struct SparkGap {
    double spark_voltage_v{1200.0};
    double arc_voltage_v{18.0};
    double arc_resistance_ohm{0.4};
    double ionization_delay_s{4.0e-9};
    GapState state{GapState::Waiting};
    double timer_s{0.0};

    void update(double voltage_v, double dt_s) noexcept {
        if (state == GapState::ArcIgnited) return;

        if (voltage_v >= spark_voltage_v) {
            state = GapState::Forming;
            timer_s += dt_s;
            if (timer_s >= ionization_delay_s) {
                state = GapState::ArcIgnited;
            }
        } else {
            state = GapState::Waiting;
            timer_s = 0.0;
        }
    }

    [[nodiscard]] constexpr bool is_arc() const noexcept {
        return state == GapState::ArcIgnited;
    }
};

struct TvsDiode {
    double breakdown_voltage_v{6.8};
    double dynamic_resistance_ohm{0.5};
    double junction_capacitance_f{15.0e-12};

    [[nodiscard]] double compute_current(double voltage_v) const noexcept {
        if (voltage_v <= breakdown_voltage_v) return 0.0;
        return (voltage_v - breakdown_voltage_v) / dynamic_resistance_ohm;
    }
};

struct DecouplingTrace {
    double series_resistance_ohm{2.2};
    double inductance_henry{25.0e-9};
};

struct SimulationResults {
    double energy_spark_gap_j{0.0};
    double energy_tvs_j{0.0};
    double energy_resistor_j{0.0};
    double peak_clamping_voltage_v{0.0};
};

class CascadeSimulator {
public:
    CascadeSimulator(SparkGap gap, TvsDiode tvs, DecouplingTrace dec) noexcept
        : gap_{gap}, tvs_{tvs}, dec_{dec} {}

    SimulationResults run(double total_time_s, double dt_s) {
        SimulationResults res{};
        double i_trace = 0.0;
        double v_tvs = 0.0;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Час [нс] | Струм ESD [A] | Напруга Gap [В] | Струм Gap [A] | Напруга TVS [В] | Стан іскровика\n";
        std::cout << "--------------------------------------------------------------------------------------------\n";

        const size_t total_steps = static_cast<size_t>(total_time_s / dt_s);

        for (size_t step = 0; step < total_steps; ++step) {
            const double t = step * dt_s;
            const double i_esd = calculate_esd_pulse(t);

            double v_gap = 0.0;
            double i_gap = 0.0;

            if (gap_.is_arc()) {
                i_gap = std::max(0.0, i_esd - i_trace);
                v_gap = gap_.arc_voltage_v + i_gap * gap_.arc_resistance_ohm;
            } else {
                i_gap = 0.0;
                const double di_dt = (i_esd - i_trace) / dt_s;
                v_gap = v_tvs + dec_.series_resistance_ohm * i_trace + dec_.inductance_henry * di_dt;
                gap_.update(v_gap, dt_s);
            }

            const double di_trace_dt = (v_gap - v_tvs - dec_.series_resistance_ohm * i_trace) / dec_.inductance_henry;
            i_trace = std::max(0.0, i_trace + di_trace_dt * dt_s);

            const double i_tvs = tvs_.compute_current(v_tvs);
            const double dv_tvs_dt = (i_trace - i_tvs) / tvs_.junction_capacitance_f;
            v_tvs += dv_tvs_dt * dt_s;

            res.peak_clamping_voltage_v = std::max(res.peak_clamping_voltage_v, v_tvs);
            res.energy_spark_gap_j += (v_gap * i_gap) * dt_s;
            res.energy_tvs_j += (v_tvs * i_tvs) * dt_s;
            res.energy_resistor_j += (i_trace * i_trace * dec_.series_resistance_ohm) * dt_s;

            if (step % 200 == 0) {
                std::cout << std::setw(7) << (t * 1e9) << "  | "
                          << std::setw(13) << i_esd << " | "
                          << std::setw(15) << v_gap << " | "
                          << std::setw(13) << i_gap << " | "
                          << std::setw(15) << v_tvs << " | "
                          << (gap_.is_arc() ? "ДУГА (ON)" : "ІЗОЛЯЦІЯ") << "\n";
            }
        }

        return res;
    }

private:
    SparkGap gap_;
    TvsDiode tvs_;
    DecouplingTrace dec_;

    [[nodiscard]] static double calculate_esd_pulse(double t_sec) noexcept {
        if (t_sec < 0.0 || t_sec > 200.0e-9) return 0.0;
        const double t_ns = t_sec * 1.0e9;
        const double i1 = 30.0 * std::exp(-t_ns / 30.0) / (1.0 + std::exp(-(t_ns - 1.0) / 0.5));
        const double i2 = 15.0 * std::exp(-t_ns / 60.0) / (1.0 + std::exp(-(t_ns - 1.0) / 1.5));
        return i1 + i2;
    }
};

int main() {
    CascadeSimulator simulator{
        SparkGap{.spark_voltage_v = 1200.0, .arc_voltage_v = 18.0, .arc_resistance_ohm = 0.4, .ionization_delay_s = 4.0e-9},
        TvsDiode{.breakdown_voltage_v = 6.8, .dynamic_resistance_ohm = 0.5, .junction_capacitance_f = 15.0e-12},
        DecouplingTrace{.series_resistance_ohm = 2.2, .inductance_henry = 25.0e-9}
    };

    const auto results = simulator.run(80.0e-9, 1.0e-11);
    const double total_energy = results.energy_spark_gap_j + results.energy_tvs_j + results.energy_resistor_j;

    std::cout << "--------------------------------------------------------------------------------------------\n";
    std::cout << "Підсумки розподілу енергії:\n";
    std::cout << "  Енергія в іскровому розряднику: " << (results.energy_spark_gap_j * 1000.0) << " мДж ("
              << (results.energy_spark_gap_j / total_energy * 100.0) << "%)\n";
    std::cout << "  Енергія в резисторі розв'язки:  " << (results.energy_resistor_j * 1000.0) << " мДж\n";
    std::cout << "  Енергія в TVS-діоді:            " << (results.energy_tvs_j * 1000.0) << " мДж ("
              << (results.energy_tvs_j / total_energy * 100.0) << "%)\n";
    std::cout << "  Пікова напруга на мікросхемі:   " << results.peak_clamping_voltage_v << " В\n";

    return 0;
}
