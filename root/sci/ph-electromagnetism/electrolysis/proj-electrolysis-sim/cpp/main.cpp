#include <iostream>
#include <iomanip>
#include <cmath>
#include <expected>
#include <string_view>

namespace electrolysis {

constexpr double FARADAY_CONST = 96485.33215; // Кл/моль
constexpr double MOLAR_GAS_VOL = 22.414;      // л/моль за НУ

struct IonProperties {
    double molar_mass_g;
    int valence;
    double density_g_cm3;
    double faraday_eff; // 0.0 .. 1.0
};

struct CellParameters {
    double area_cm2;
    double distance_cm;
    double resist_ohm_cm;
    double bubble_fraction{0.05};
    double e0_cell_v;
    double tafel_a_anode;
    double tafel_b_anode;
    double tafel_a_cath;
    double tafel_b_cath;
};

struct SimulationResult {
    double total_charge_c;
    double mass_deposited_g;
    double thickness_um;
    double gas_volume_liters;
    double overpotential_anode;
    double overpotential_cath;
    double ohmic_drop_v;
    double applied_voltage_v;
    double total_energy_wh;
    double specific_energy_kwh_kg;
    double energy_efficiency_pct;
};

enum class SimulationError {
    InvalidCurrentOrTime,
    InvalidGeometry,
    ZeroDensity
};

class ElectrolysisSimulator {
public:
    [[nodiscard]] static std::expected<SimulationResult, SimulationError> 
    compute(const IonProperties& ion, const CellParameters& cell,
            double current_a, double time_sec) noexcept 
    {
        if (current_a <= 0.0 || time_sec <= 0.0) {
            return std::unexpected(SimulationError::InvalidCurrentOrTime);
        }
        if (cell.area_cm2 <= 0.0 || cell.distance_cm <= 0.0 || ion.density_g_cm3 <= 0.0) {
            return std::unexpected(SimulationError::InvalidGeometry);
        }

        SimulationResult res{};

        // 1. Закон Фарадея
        res.total_charge_c = current_a * time_sec;
        const double mass_theo = (ion.molar_mass_g * res.total_charge_c) / 
                                 (ion.valence * FARADAY_CONST);
        res.mass_deposited_g = mass_theo * ion.faraday_eff;

        // 2. Геометрія осадженого шару
        const double volume_cm3 = res.mass_deposited_g / ion.density_g_cm3;
        res.thickness_um = (volume_cm3 / cell.area_cm2) * 10000.0;

        // 3. Газоутворення
        const double moles_e = res.total_charge_c / FARADAY_CONST;
        const double moles_gas = (moles_e / 2.0) * (1.0 - ion.faraday_eff);
        res.gas_volume_liters = moles_gas * MOLAR_GAS_VOL;

        // 4. Кінетика та перенапруга Тафеля
        const double j = current_a / cell.area_cm2;
        res.overpotential_anode = std::max(0.0, cell.tafel_a_anode + cell.tafel_b_anode * std::log10(j));
        res.overpotential_cath  = std::max(0.0, cell.tafel_a_cath  + cell.tafel_b_cath  * std::log10(j));

        // 5. Омічні втрати в рідині з урахуванням ефекту Бруггемана
        const double eps = std::clamp(cell.bubble_fraction, 0.0, 0.4);
        const double eff_resist = cell.resist_ohm_cm / std::pow(1.0 - eps, 1.5);
        const double r_sol = (eff_resist * cell.distance_cm) / cell.area_cm2;
        res.ohmic_drop_v = current_a * r_sol;

        // 6. Повна прикладена напруга
        res.applied_voltage_v = cell.e0_cell_v + res.overpotential_anode + 
                                 res.overpotential_cath + res.ohmic_drop_v;

        // 7. Енергетичні характеристики
        res.total_energy_wh = (res.applied_voltage_v * current_a * time_sec) / 3600.0;
        res.specific_energy_kwh_kg = (res.mass_deposited_g > 0.0) 
            ? (res.total_energy_wh / 1000.0) / (res.mass_deposited_g / 1000.0)
            : 0.0;

        res.energy_efficiency_pct = ion.faraday_eff * (cell.e0_cell_v / res.applied_voltage_v) * 100.0;

        return res;
    }
};

} // namespace electrolysis

int main() {
    using namespace electrolysis;

    const IonProperties nickel{
        .molar_mass_g = 58.6934,
        .valence = 2,
        .density_g_cm3 = 8.908,
        .faraday_eff = 0.95
    };

    const CellParameters bath{
        .area_cm2 = 500.0,
        .distance_cm = 8.0,
        .resist_ohm_cm = 5.0,
        .bubble_fraction = 0.10,
        .e0_cell_v = 1.25,
        .tafel_a_anode = 0.40,
        .tafel_b_anode = 0.10,
        .tafel_a_cath = 0.20,
        .tafel_b_cath = 0.09
    };

    auto sim_res = ElectrolysisSimulator::compute(nickel, bath, 25.0, 7200.0);

    if (sim_res) {
        const auto& r = *sim_res;
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Симуляція нікелювання (C++23) ===\n";
        std::cout << "Маса осадженого Ni:   " << r.mass_deposited_g << " г\n";
        std::cout << "Товщина покриття:     " << r.thickness_um << " мкм\n";
        std::cout << "Виділений H2:         " << r.gas_volume_liters << " л\n";
        std::cout << "Анодна перенапруга:   " << r.overpotential_anode << " В\n";
        std::cout << "Катодна перенапруга:  " << r.overpotential_cath << " В\n";
        std::cout << "Омічне падіння IR:    " << r.ohmic_drop_v << " В\n";
        std::cout << "Прикладена напруга:   " << r.applied_voltage_v << " В\n";
        std::cout << "Питома енергія:       " << r.specific_energy_kwh_kg << " кВт·год/кг\n";
        std::cout << "Енергетичний ККД:     " << r.energy_efficiency_pct << " %\n";
    }

    return 0;
}
