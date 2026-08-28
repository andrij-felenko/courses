#include <iostream>
#include <cmath>
#include <vector>
#include <span>
#include <string_view>
#include <iomanip>

struct GAAFETConfig {
    double nanosheet_width_nm{35.0};
    double nanosheet_thickness_nm{5.0};
    double gate_length_nm{12.0};
    std::size_t sheet_count{3};
    double nominal_vdd_v{0.70};
    double frontside_pdn_resistance_ohm{85.0};
    double backside_pdn_resistance_ohm{18.0};
};

struct SimulationResult {
    double total_effective_width_nm{0.0};
    double drive_current_ma{0.0};
    double frontside_ir_drop_mv{0.0};
    double backside_ir_drop_mv{0.0};
    double effective_vdd_frontside_v{0.0};
    double effective_vdd_backside_v{0.0};
    double performance_gain_percent{0.0};
};

class GAAFETPowerNetworkSimulator {
public:
    [[nodiscard]] static SimulationResult compute(const GAAFETConfig& cfg) noexcept {
        SimulationResult out;

        // 1. Обчислення повної ефективної провідної ширини наношарів
        const double perimeter = 2.0 * (cfg.nanosheet_width_nm + cfg.nanosheet_thickness_nm);
        out.total_effective_width_nm = static_cast<double>(cfg.sheet_count) * perimeter;

        // 2. Номінальний струм насичення
        constexpr double CurrentDensityMaPerUm = 1.42;
        const double nominal_current_ma = (out.total_effective_width_nm / 1000.0) *
                                          CurrentDensityMaPerUm;

        // 3. Розрахунок резистивного падіння напруги IR-drop
        out.frontside_ir_drop_mv = (nominal_current_ma * 1e-3) *
                                   cfg.frontside_pdn_resistance_ohm * 1000.0;
        out.effective_vdd_frontside_v = cfg.nominal_vdd_v - (out.frontside_ir_drop_mv / 1000.0);

        out.backside_ir_drop_mv = (nominal_current_ma * 1e-3) *
                                  cfg.backside_pdn_resistance_ohm * 1000.0;
        out.effective_vdd_backside_v = cfg.nominal_vdd_v - (out.backside_ir_drop_mv / 1000.0);

        // 4. Оцінка швидкодії за реальної робочої напруги
        constexpr double ThresholdVoltageV = 0.22;
        const double overdrive_nominal = cfg.nominal_vdd_v - ThresholdVoltageV;
        const double i_front = nominal_current_ma *
                               ((out.effective_vdd_frontside_v - ThresholdVoltageV) / overdrive_nominal);
        const double i_back = nominal_current_ma *
                              ((out.effective_vdd_backside_v - ThresholdVoltageV) / overdrive_nominal);

        out.drive_current_ma = i_back;
        out.performance_gain_percent = ((i_back - i_front) / i_front) * 100.0;

        return out;
    }
};

int main() {
    const std::vector<std::pair<std::string_view, GAAFETConfig>> scenarios = {
        {"3-Nanosheet Standard (TSMC N2 / Samsung 3GAP)", GAAFETConfig{.sheet_count = 3}},
        {"4-Nanosheet RibbonFET (Intel 18A)           ", GAAFETConfig{.sheet_count = 4}}
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== GAAFET Electrostatic & Power Delivery Network Analysis ===\n";
    for (const auto& [name, cfg] : scenarios) {
        const auto res = GAAFETPowerNetworkSimulator::compute(cfg);
        std::cout << "[" << name << "]\n"
                  << "  W_eff: " << res.total_effective_width_nm << " nm | I_drive: "
                  << res.drive_current_ma << " mA\n"
                  << "  Frontside PDN Drop : " << res.frontside_ir_drop_mv << " mV (V_eff = "
                  << res.effective_vdd_frontside_v << " V)\n"
                  << "  Backside PowerVia  : " << res.backside_ir_drop_mv << " mV (V_eff = "
                  << res.effective_vdd_backside_v << " V)\n"
                  << "  Net Drive Gain     : +" << res.performance_gain_percent << " %\n\n";
    }
    return 0;
}
