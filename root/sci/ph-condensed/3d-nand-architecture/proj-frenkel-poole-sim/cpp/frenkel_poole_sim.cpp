// frenkel_poole_sim.cpp — Ідіоматична реалізація симулятора на C++17
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

namespace Physics {
    constexpr double Q_ELEM   = 1.602176634e-19; // Кл
    constexpr double KB_BOLTZ = 1.380649e-23;    // Дж/К
    constexpr double EPS_0    = 8.854187817e-12; // Ф/м
    constexpr double PI_VAL   = 3.14159265358979323846;
}

struct NitrideMaterial {
    double eps_r{5.5};
    double trap_depth_ev{1.05};
    double c_leakage{1.5e-6};
};

struct SimulationResult {
    double field_mv_cm;
    double barrier_reduction_ev;
    double current_density_a_cm2;
    double retention_years;
};

class PooleFrenkelSimulator {
public:
    explicit PooleFrenkelSimulator(NitrideMaterial mat) : material_(mat) {}

    [[nodiscard]] SimulationResult calculatePoint(double field_mv_cm, double temp_celsius) const {
        using namespace Physics;
        
        const double temp_k = temp_celsius + 273.15;
        const double field_v_m = field_mv_cm * 1e8;
        const double eps_i = material_.eps_r * EPS_0;

        // Зниження потенціального бар'єра dPhi
        const double dphi_joules = std::sqrt((Q_ELEM * Q_ELEM * Q_ELEM * field_v_m) / (PI_VAL * eps_i));
        const double dphi_ev = dphi_joules / Q_ELEM;

        const double effective_phi_joules = std::max(0.0, (material_.trap_depth_ev * Q_ELEM) - dphi_joules);

        // Густина струму J_PF у А/м²
        const double exponent = -effective_phi_joules / (KB_BOLTZ * temp_k);
        const double j_pf_m2 = material_.c_leakage * field_v_m * std::exp(exponent);
        const double j_pf_cm2 = j_pf_m2 / 1e4;

        // Оцінка утримання заряду
        constexpr double q_density_cm2 = 1.0e-5; // Кл/см²
        const double retention_sec = (j_pf_cm2 > 1e-30) ? (q_density_cm2 / j_pf_cm2) : 1e15;
        const double retention_years = retention_sec / (365.25 * 86400.0);

        return {field_mv_cm, dphi_ev, j_pf_cm2, retention_years};
    }

    [[nodiscard]] std::vector<SimulationResult> runSweep(double min_field, double max_field, 
                                                         double step, double temp_celsius) const {
        std::vector<SimulationResult> results;
        results.reserve(static_cast<size_t>((max_field - min_field) / step) + 1);

        for (double f = min_field; f <= max_field + 1e-9; f += step) {
            results.push_back(calculatePoint(f, temp_celsius));
        }
        return results;
    }

private:
    NitrideMaterial material_;
};

int main() {
    NitrideMaterial si3n4{5.5, 1.05, 1.5e-6};
    PooleFrenkelSimulator sim(si3n4);

    constexpr double test_temp = 85.0; // °C
    auto results = sim.runSweep(0.5, 4.0, 0.5, test_temp);

    std::cout << "=== C++17 Моделювання витоку Френкеля-Пуля (T = " << test_temp << " °C) ===\n\n";
    std::cout << std::left << std::setw(12) << "E (МВ/см)"
              << " | " << std::setw(14) << "dPhi (еВ)"
              << " | " << std::setw(16) << "J_PF (А/см²)"
              << " | " << std::setw(16) << "Retention (роки)" << "\n";
    std::cout << std::string(68, '-') << "\n";

    for (const auto& res : results) {
        std::cout << std::left << std::setw(12) << std::fixed << std::setprecision(2) << res.field_mv_cm
                  << " | " << std::setw(14) << std::setprecision(4) << res.barrier_reduction_ev
                  << " | " << std::setw(16) << std::scientific << std::setprecision(4) << res.current_density_a_cm2
                  << " | " << std::setw(16) << std::scientific << std::setprecision(4) << res.retention_years << "\n";
    }

    return 0;
}
