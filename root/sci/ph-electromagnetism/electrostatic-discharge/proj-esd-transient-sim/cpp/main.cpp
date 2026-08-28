#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <expected>
#include <string_view>

namespace esd_sim {

struct CircuitParameters {
    double capacitance_farads{150e-12};
    double inductance_henry{10e-9};
    double resistance_ohms{330.0};
    double initial_voltage_volts{8000.0};
};

struct TvsParameters {
    double breakdown_voltage{6.8};
    double dynamic_resistance{0.25};
    double parasitic_capacitance{0.3e-12};
};

struct SimulationResult {
    double peak_current_ampere{0.0};
    double max_clamping_voltage{0.0};
    double energy_tvs_joules{0.0};
    double duration_nanoseconds{0.0};
    std::vector<std::pair<double, double>> time_current_series{};
};

enum class SimulationError {
    InvalidParameters,
    NumericalInstability
};

class EsdTransientSolver {
public:
    explicit EsdTransientSolver(CircuitParameters circuit, TvsParameters tvs)
        : m_circuit(circuit), m_tvs(tvs) {}

    [[nodiscard]] std::expected<SimulationResult, SimulationError> solve(
        double sim_time_ns = 100.0, 
        double dt_ps = 1.0) const 
    {
        if (m_circuit.capacitance_farads <= 0.0 || m_circuit.inductance_henry <= 0.0) {
            return std::unexpected(SimulationError::InvalidParameters);
        }

        SimulationResult result;
        const double dt = dt_ps * 1e-12;
        const double total_time = sim_time_ns * 1e-9;

        double v_cap = m_circuit.initial_voltage_volts;
        double current = 0.0;
        double time = 0.0;

        result.time_current_series.reserve(static_cast<size_t>(sim_time_ns / (dt_ps * 1e-3)));

        while (time < total_time && v_cap > 0.05) {
            const double v_tvs = compute_tvs_voltage(current);

            const double dv_cap = -current / m_circuit.capacitance_farads;
            const double di_dt = (v_cap - current * m_circuit.resistance_ohms - v_tvs) 
                                / m_circuit.inductance_henry;

            v_cap += dv_cap * dt;
            current += di_dt * dt;
            time += dt;

            if (current < 0.0) {
                current = 0.0;
            }

            result.peak_current_ampere = std::max(result.peak_current_ampere, current);
            result.max_clamping_voltage = std::max(result.max_clamping_voltage, v_tvs);
            result.energy_tvs_joules += (v_tvs * current) * dt;

            result.time_current_series.emplace_back(time * 1e9, current);
        }

        result.duration_nanoseconds = time * 1e9;
        return result;
    }

private:
    [[nodiscard]] double compute_tvs_voltage(double current) const noexcept {
        const double abs_i = std::abs(current);
        if (abs_i < 1e-6) {
            return 0.0;
        }
        return m_tvs.breakdown_voltage + abs_i * m_tvs.dynamic_resistance;
    }

    CircuitParameters m_circuit;
    TvsParameters m_tvs;
};

} // namespace esd_sim

int main() {
    using namespace esd_sim;

    const CircuitParameters iec_hbm{150e-12, 10e-9, 330.0, 8000.0};
    const TvsParameters tvs_diode{6.8, 0.25, 0.3e-12};

    const EsdTransientSolver solver(iec_hbm, tvs_diode);
    const auto outcome = solver.solve(100.0, 1.0);

    if (!outcome) {
        std::cerr << "Помилка розрахунку симуляції ESD!\n";
        return 1;
    }

    const auto& res = outcome.value();
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Обчислення симулятора ESD (C++23) ===\n";
    std::cout << "Піковий струм розряду (I_peak):    " << res.peak_current_ampere << " А\n";
    std::cout << "Напруга обмеження (V_clamp):       " << res.max_clamping_voltage << " В\n";
    std::cout << "Енергія розсіяна TVS (E_tvs):       " << (res.energy_tvs_joules * 1000.0) << " мДж\n";
    std::cout << "Тривалість імпульсу:              " << res.duration_nanoseconds << " нс\n";

    return 0;
}
