#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <optional>
#include <string>

struct EnergyStorage {
    double v_oc_max{4.2};    // Напруга 100% SOC (В)
    double v_oc_min{3.0};    // Напруга 0% SOC (В)
    double v_cutoff{2.8};    // Напруга відсічки (В)
    double r_in{0.025};      // Внутрішній опір (Ом)
    double capacity_ah{3.0}; // Номінальна ємність (А·год)
    double mass_kg{0.048};   // Маса елемента (кг)

    [[nodiscard]] constexpr double get_emative_force(double soc) const noexcept {
        return v_oc_min + soc * (v_oc_max - v_oc_min);
    }
};

struct RagonePoint {
    double p_specific_w_kg{0.0};  // Питома потужність (Вт/кг)
    double e_specific_wh_kg{0.0}; // Питома енергія (Вт·год/кг)
    double discharge_time_s{0.0}; // Час розряджання (секунди)
};

class RagoneSimulator {
public:
    explicit RagoneSimulator(EnergyStorage device) : device_(std::move(device)) {}

    [[nodiscard]] std::optional<RagonePoint> simulate_constant_power(double p_const, double dt_sec = 0.05) const {
        double soc = 1.0;
        const double q_total_as = device_.capacity_ah * 3600.0;
        double time_elapsed = 0.0;
        double energy_joules = 0.0;

        while (soc > 0.0) {
            const double v_oc = device_.get_emative_force(soc);
            const double discr = v_oc * v_oc - 4.0 * device_.r_in * p_const;

            if (discr < 0.0) {
                break; // Перевищення межі P_max
            }

            const double current = (v_oc - std::sqrt(discr)) / (2.0 * device_.r_in);
            const double v_terminal = v_oc - current * device_.r_in;

            if (v_terminal <= device_.v_cutoff) {
                break; // Відсічка за напругою
            }

            soc -= (current * dt_sec) / q_total_as;
            energy_joules += p_const * dt_sec;
            time_elapsed += dt_sec;
        }

        if (time_elapsed <= 0.0) {
            return std::nullopt;
        }

        return RagonePoint{
            .p_specific_w_kg = p_const / device_.mass_kg,
            .e_specific_wh_kg = (energy_joules / 3600.0) / device_.mass_kg,
            .discharge_time_s = time_elapsed
        };
    }

    [[nodiscard]] std::vector<RagonePoint> generate_ragone_curve(double p_start, double p_end, double factor) const {
        std::vector<RagonePoint> points;
        for (double p = p_start; p <= p_end; p *= factor) {
            if (auto pt = simulate_constant_power(p); pt.has_value()) {
                points.push_back(*pt);
            }
        }
        return points;
    }

private:
    EnergyStorage device_;
};

int main() {
    const EnergyStorage nmc_cell{
        .v_oc_max = 4.2,
        .v_oc_min = 3.0,
        .v_cutoff = 2.8,
        .r_in = 0.025,
        .capacity_ah = 3.0,
        .mass_kg = 0.048
    };

    const RagoneSimulator simulator(nmc_cell);
    const auto curve = simulator.generate_ragone_curve(1.0, 120.0, 1.6);

    std::cout << "=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ДІАГРАМИ РАГОНЕ (C++) ===\n";
    std::cout << std::setw(25) << "Питома потужність (Вт/кг)" << " | "
              << std::setw(26) << "Питома енергія (Вт·год/кг)" << " | "
              << std::setw(15) << "Час розряду (с)" << "\n";
    std::cout << std::string(72, '-') << "\n";

    for (const auto& pt : curve) {
        std::cout << std::fixed << std::setprecision(2)
                  << std::setw(25) << pt.p_specific_w_kg << " | "
                  << std::setw(26) << pt.e_specific_wh_kg << " | "
                  << std::setw(15) << std::setprecision(1) << pt.discharge_time_s << "\n";
    }

    return 0;
}
