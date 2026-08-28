#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>
#include <expected>

struct HarvesterSource {
    double power_uW;       // Середня потужність збирача (мкВт)
    double mpp_voltage_V;   // Напруга в точці MPP (В)
};

struct NodeEnergyProfile {
    double cap_uF;         // Ємність накопичувача (мкФ)
    double v_chg_V;        // Поріг увімкнення (В)
    double v_dis_V;        // Поріг вимкнення (В)
    double i_leak_uA;      // Струм витоку (мкА)
    double i_sleep_uA;     // Струм глибокого сну (мкА)
    double i_active_mA;    // Струм передачі (мА)
    double t_active_ms;    // Тривалість імпульсу (мс)
};

struct SimulationReport {
    double usable_energy_uJ;
    double active_energy_uJ;
    double recharge_time_s;
    double packet_rate_per_min;
};

enum class SimError {
    InsufficientCapacitance,
    HarvestingPowerBelowLosses
};

class EnergyHarvesterModel {
public:
    static std::expected<SimulationReport, SimError> evaluate(
        const HarvesterSource& src, 
        const NodeEnergyProfile& node,
        double pmic_efficiency = 0.85) noexcept 
    {
        const double v_delta_sq = (node.v_chg_V * node.v_chg_V) - 
                                  (node.v_dis_V * node.v_dis_V);
        const double usable_energy = 0.5 * node.cap_uF * v_delta_sq;
        
        const double v_avg = 0.5 * (node.v_chg_V + node.v_dis_V);
        const double active_energy = v_avg * node.i_active_mA * node.t_active_ms;
        
        if (usable_energy < active_energy) {
            return std::unexpected(SimError::InsufficientCapacitance);
        }
        
        const double i_harv_avg = (src.power_uW * pmic_efficiency) / v_avg;
        const double i_net_charge = i_harv_avg - node.i_sleep_uA - node.i_leak_uA;
        
        if (i_net_charge <= 0.0) {
            return std::unexpected(SimError::HarvestingPowerBelowLosses);
        }
        
        const double delta_q = node.cap_uF * (node.v_chg_V - node.v_dis_V);
        const double recharge_time = delta_q / i_net_charge;
        
        return SimulationReport{
            .usable_energy_uJ = usable_energy,
            .active_energy_uJ = active_energy,
            .recharge_time_s = recharge_time,
            .packet_rate_per_min = 60.0 / recharge_time
        };
    }
};

void print_result(std::string_view name, 
                  const std::expected<SimulationReport, SimError>& res) {
    std::cout << "Джерело [" << name << "]:\n";
    if (res.has_value()) {
        const auto& r = res.value();
        std::cout << "  -> Час заряду: " << std::fixed << std::setprecision(2) 
                  << r.recharge_time_s << " с (" 
                  << r.packet_rate_per_min << " пакетів/хв)\n";
    } else {
        if (res.error() == SimError::InsufficientCapacitance) {
            std::cout << "  -> Помилка: ємність конденсатора замала для імпульсу!\n";
        } else {
            std::cout << "  -> Помилка: надходження енергії менше за фонові витоки!\n";
        }
    }
}

int main() {
    constexpr HarvesterSource solar_indoor{ .power_uW = 280.0, .mpp_voltage_V = 2.4 };
    constexpr HarvesterSource rf_ambient{ .power_uW = 3.5, .mpp_voltage_V = 0.45 };
    
    constexpr NodeEnergyProfile node{
        .cap_uF = 470.0,
        .v_chg_V = 3.3,
        .v_dis_V = 2.4,
        .i_leak_uA = 0.8,
        .i_sleep_uA = 0.9,
        .i_active_mA = 16.0,
        .t_active_ms = 10.0
    };
    
    auto res_solar = EnergyHarvesterModel::evaluate(solar_indoor, node);
    auto res_rf = EnergyHarvesterModel::evaluate(rf_ambient, node);
    
    std::cout << "=== СИМУЛЯЦІЯ БЕЗБАТАРЕЙНОГО ЖИВЛЕННЯ (C++23) ===\n\n";
    print_result("Офісне світло a-Si (280 мкВт)", res_solar);
    print_result("Розсіяний Wi-Fi ефір (3.5 мкВт)", res_rf);
    
    return 0;
}
