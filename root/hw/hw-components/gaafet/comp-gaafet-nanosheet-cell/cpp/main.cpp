#include <iostream>
#include <cmath>
#include <vector>
#include <span>
#include <string_view>
#include <iomanip>

struct NanosheetGeometry {
    double width_nm{35.0};
    double thickness_nm{5.0};
    double gate_length_nm{12.0};
    std::size_t sheet_count{3};
    double eot_nm{0.8};
    double spacer_length_nm{5.5};
    double spacer_dielectric_k{4.2};
    double supply_voltage_v{0.7};
};

struct StandardCellMetrics {
    double effective_width_nm{0.0};
    double channel_capacitance_ff{0.0};
    double inner_spacer_capacitance_ff{0.0};
    double total_gate_capacitance_ff{0.0};
    double drive_current_ma{0.0};
    double propagation_delay_ps{0.0};
    double self_heating_delta_t_c{0.0};
};

class NanosheetCellAnalyzer {
public:
    static constexpr double VacuumPermittivity = 8.854187e-12; // F/m
    static constexpr double Sio2RelativePermittivity = 3.9;

    [[nodiscard]] static StandardCellMetrics analyze(const NanosheetGeometry& geom) noexcept {
        StandardCellMetrics out;

        // 1. Повна ефективна ширина каналу
        const double perimeter = 2.0 * (geom.width_nm + geom.thickness_nm);
        out.effective_width_nm = static_cast<double>(geom.sheet_count) * perimeter;

        // 2. Ємність каналу інверсії
        const double c_ox_density = (Sio2RelativePermittivity * VacuumPermittivity) /
                                    (geom.eot_nm * 1e-9);
        const double channel_area_m2 = (out.effective_width_nm * 1e-9) *
                                       (geom.gate_length_nm * 1e-9);
        out.channel_capacitance_ff = (channel_area_m2 * c_ox_density) * 1e15;

        // 3. Паразитна ємність внутрішніх спейсерів
        constexpr double VerticalSuspensionGapNm = 9.0;
        const double eps_spacer = geom.spacer_dielectric_k * VacuumPermittivity;
        const double single_spacer_cap = eps_spacer * (geom.width_nm * 1e-9) *
                                         (VerticalSuspensionGapNm * 1e-9) /
                                         (geom.spacer_length_nm * 1e-9);

        const auto spacer_layers = static_cast<double>(geom.sheet_count - 1);
        out.inner_spacer_capacitance_ff = (2.0 * spacer_layers * single_spacer_cap) * 1e15;
        out.total_gate_capacitance_ff = out.channel_capacitance_ff * 1.15 +
                                        out.inner_spacer_capacitance_ff;

        // 4. Струм насичення I_on
        constexpr double BaseDriveDensityMaPerUm = 1.45;
        out.drive_current_ma = (out.effective_width_nm / 1000.0) *
                               BaseDriveDensityMaPerUm *
                               (geom.supply_voltage_v / 0.7);

        // 5. Власна затримка вентиля
        out.propagation_delay_ps = (out.total_gate_capacitance_ff * 1e-15 * geom.supply_voltage_v /
                                   (out.drive_current_ma * 1e-3)) * 1e12;

        // 6. Оцінка локального саморозігріву
        constexpr double BaseThermalResistancePerSheet = 85.0; // K/mW
        const double p_diss_mw = out.drive_current_ma * geom.supply_voltage_v * 0.15;
        const double r_th_stack = BaseThermalResistancePerSheet / static_cast<double>(geom.sheet_count);
        out.self_heating_delta_t_c = p_diss_mw * r_th_stack;

        return out;
    }
};

int main() {
    const std::vector<std::pair<std::string_view, NanosheetGeometry>> library_cells = {
        {"High-Performance (HP)  ", NanosheetGeometry{.width_nm = 45.0, .sheet_count = 3}},
        {"Standard-Density (HD)  ", NanosheetGeometry{.width_nm = 30.0, .sheet_count = 3}},
        {"Ultra-High-Density (uHD)", NanosheetGeometry{.width_nm = 18.0, .sheet_count = 3}}
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== GAAFET Nanosheet Standard Cell Library Analysis ===\n";
    for (const auto& [cell_name, config] : library_cells) {
        const auto metrics = NanosheetCellAnalyzer::analyze(config);
        std::cout << "[" << cell_name << "] W_eff: " << std::setw(5) << metrics.effective_width_nm
                  << " nm | I_on: " << metrics.drive_current_ma << " mA | Delay: "
                  << metrics.propagation_delay_ps << " ps | SHE: +"
                  << metrics.self_heating_delta_t_c << " °C\n";
    }
    return 0;
}
