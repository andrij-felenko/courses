// ground_fault_sim.cpp — Idiomatic C++20 Fault Simulation & Safety Verification

#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <format>
#include <cmath>

enum class EarthingSystem {
    TnS,
    TnCS,
    Tt
};

struct GridParameters {
    double phase_voltage{230.0};          // V
    double r_trafo{0.05};                 // Ohm
    double r_phase_wire{0.35};            // Ohm
    double r_pe_wire{0.35};               // Ohm
    double r_source_ground{2.0};          // Ohm (R0)
    double r_equip_ground{4.0};           // Ohm (Re)
    double pe_cross_section_mm2{1.5};     // mm²
};

enum class McbCurve { B, C, D };

struct ProtectionDevice {
    double mcb_nominal_current{16.0};     // A
    McbCurve curve{McbCurve::C};
    double rcd_trip_current_ma{30.0};     // mA (0 if absent)
    double trip_time_sec{0.4};            // s

    [[nodiscard]] constexpr double instant_trip_multiplier() const noexcept {
        switch (curve) {
            case McbCurve::B: return 5.0;
            case McbCurve::C: return 10.0;
            case McbCurve::D: return 20.0;
        }
        return 10.0;
    }
};

struct FaultResult {
    double fault_current;        // A
    double touch_voltage;        // V
    double min_pe_section_req;   // mm²
    bool mcb_tripped_fast;
    bool rcd_tripped;
    bool thermal_safe;
    bool safety_passed;
};

enum class SimulationError {
    InvalidZeroImpedance,
    MissingRcdInTtSystem,
    ThermalOverload
};

class EarthingSimulator {
public:
    [[nodiscard]] static std::expected<FaultResult, SimulationError> 
    simulate(EarthingSystem system, const GridParameters& grid, const ProtectionDevice& prot) {
        FaultResult res{};
        constexpr double k_cu = 115.0; // Copper PVC thermal constant

        if (system == EarthingSystem::TnS || system == EarthingSystem::TnCS) {
            const double z_loop = grid.r_trafo + grid.r_phase_wire + grid.r_pe_wire;
            if (z_loop <= 1e-6) {
                return std::unexpected(SimulationError::InvalidZeroImpedance);
            }

            res.fault_current = grid.phase_voltage / z_loop;
            res.touch_voltage = res.fault_current * grid.r_pe_wire;

            const double trip_threshold = prot.mcb_nominal_current * prot.instant_trip_multiplier();
            res.mcb_tripped_fast = (res.fault_current >= trip_threshold);
            res.rcd_tripped = (prot.rcd_trip_current_ma > 0.0) && 
                              ((res.fault_current * 1000.0) >= prot.rcd_trip_current_ma);

            const double t_trip = res.mcb_tripped_fast ? 0.02 : prot.trip_time_sec;
            res.min_pe_section_req = (res.fault_current * std::sqrt(t_trip)) / k_cu;
            res.thermal_safe = (grid.pe_cross_section_mm2 >= res.min_pe_section_req);

            if (!res.thermal_safe) {
                return std::unexpected(SimulationError::ThermalOverload);
            }

            res.safety_passed = (res.mcb_tripped_fast || res.rcd_tripped) && res.thermal_safe;
            return res;

        } else if (system == EarthingSystem::Tt) {
            const double z_loop = grid.r_trafo + grid.r_phase_wire + 
                                  grid.r_equip_ground + grid.r_source_ground;
            if (z_loop <= 1e-6) {
                return std::unexpected(SimulationError::InvalidZeroImpedance);
            }

            res.fault_current = grid.phase_voltage / z_loop;
            res.touch_voltage = res.fault_current * grid.r_equip_ground;

            const double trip_threshold = prot.mcb_nominal_current * prot.instant_trip_multiplier();
            res.mcb_tripped_fast = (res.fault_current >= trip_threshold);

            if (prot.rcd_trip_current_ma <= 0.0) {
                return std::unexpected(SimulationError::MissingRcdInTtSystem);
            }

            const double rcd_trip_a = prot.rcd_trip_current_ma / 1000.0;
            res.rcd_tripped = (res.fault_current >= rcd_trip_a);
            const bool voltage_safe = (grid.r_equip_ground * rcd_trip_a) <= 50.0;

            constexpr double t_trip = 0.03;
            res.min_pe_section_req = (res.fault_current * std::sqrt(t_trip)) / k_cu;
            res.thermal_safe = (grid.pe_cross_section_mm2 >= res.min_pe_section_req);

            if (!res.thermal_safe) {
                return std::unexpected(SimulationError::ThermalOverload);
            }

            res.safety_passed = res.rcd_tripped && voltage_safe && res.thermal_safe;
            return res;
        }

        return std::unexpected(SimulationError::InvalidZeroImpedance);
    }
};

void print_simulation_report(std::string_view title, 
                             const std::expected<FaultResult, SimulationError>& outcome) {
    std::cout << std::format("=== {} ===\n", title);
    if (!outcome) {
        std::cout << "ПОМИЛКА СИМУЛЯЦІЇ: ";
        switch (outcome.error()) {
            case SimulationError::InvalidZeroImpedance:
                std::cout << "Нульовий опір петлі замикання!\n";
                break;
            case SimulationError::MissingRcdInTtSystem:
                std::cout << "КРИТИЧНЕ ПОРУШЕННЯ: Система TT вимагає обов'язкового ПЗВ!\n";
                break;
            case SimulationError::ThermalOverload:
                std::cout << "ТЕРМІЧНЕ ПЕРЕВАНТАЖЕННЯ: Переріз PE провідника недостатній!\n";
                break;
        }
        std::cout << "Статус безпеки: НЕБЕЗПЕЧНО (ЗАБОРОНЕНО КСП)\n\n";
        return;
    }

    const auto& res = outcome.value();
    std::cout << std::format("Струм замикання I_f:   {:.2f} А\n", res.fault_current);
    std::cout << std::format("Напруга дотику U_t:    {:.2f} В\n", res.touch_voltage);
    std::cout << std::format("Необхідний переріз PE: {:.2f} мм²\n", res.min_pe_section_req);
    std::cout << std::format("Швидке вимкнення MCB:  {}\n", res.mcb_tripped_fast ? "ТАК" : "НІ");
    std::cout << std::format("Спрацювання ПЗВ (RCD): {}\n", res.rcd_tripped ? "ТАК" : "НІ");
    std::cout << std::format("Термічна стійкість PE: {}\n", res.thermal_safe ? "НОРМА" : "ПЕРЕГРІВ!");
    std::cout << std::format("Статус безпеки:        {}\n\n", 
                             res.safety_passed ? "БЕЗПЕЧНО (НОРМА)" : "НЕБЕЗПЕЧНО (АВАРІЯ!)");
}

int main() {
    GridParameters grid_tn{};
    ProtectionDevice prot_16c{.mcb_nominal_current = 16.0, .curve = McbCurve::C, .rcd_trip_current_ma = 30.0};

    auto res_tn = EarthingSimulator::simulate(EarthingSystem::TnS, grid_tn, prot_16c);
    print_simulation_report("C++20: Симуляція у системі TN-S", res_tn);

    GridParameters grid_tt = grid_tn;
    grid_tt.r_equip_ground = 15.0; // 15 Ohm local earth electrode

    auto res_tt = EarthingSimulator::simulate(EarthingSystem::Tt, grid_tt, prot_16c);
    print_simulation_report("C++20: Симуляція у системі TT (з ПЗВ 30 мА)", res_tt);

    ProtectionDevice prot_no_rcd = prot_16c;
    prot_no_rcd.rcd_trip_current_ma = 0.0;

    auto res_tt_bad = EarthingSimulator::simulate(EarthingSystem::Tt, grid_tt, prot_no_rcd);
    print_simulation_report("C++20: Симуляція у системі TT (БЕЗ ПЗВ)", res_tt_bad);

    return 0;
}
