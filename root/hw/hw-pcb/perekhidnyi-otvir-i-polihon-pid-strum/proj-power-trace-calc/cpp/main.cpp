#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>

namespace pcb::power {

// Базові фізичні константи
inline constexpr double copper_rho_20c_ohm_mm = 1.72e-5; // Ом·мм при 20 °C
inline constexpr double copper_tcr_per_c       = 0.00393; // 1/°C
inline constexpr double mils_per_mm            = 39.37007874;

enum class LayerType {
    External, // Зовнішній шар
    Internal  // Внутрішній шар
};

enum class CalcError {
    InvalidCurrent,
    InvalidTemperatureRise,
    InvalidGeometry
};

struct TraceParams {
    double current_a{1.0};
    double temp_rise_c{20.0};
    double ambient_temp_c{25.0};
    double copper_oz{1.0};       // 1 oz = 0.035 мм
    LayerType layer{LayerType::External};
    double length_mm{10.0};
};

struct ViaParams {
    double drill_diam_mm{0.3};
    double plating_thickness_mm{0.025};
    double board_thickness_mm{1.6};
    double max_current_per_via_a{1.8};
};

struct PowerRailAnalysis {
    double required_width_mm{};
    double required_width_mils{};
    double trace_resistance_ohm{};
    double voltage_drop_trace_v{};
    double power_loss_trace_w{};
    int    required_via_count{};
    double via_array_res_ohm{};
    double voltage_drop_vias_v{};
    double total_voltage_drop_v{};
    double total_power_loss_w{};
};

[[nodiscard]] constexpr auto calculate_power_rail(
    const TraceParams& trace,
    const ViaParams& via
) noexcept -> std::expected<PowerRailAnalysis, CalcError>
{
    if (trace.current_a <= 0.0) {
        return std::unexpected(CalcError::InvalidCurrent);
    }
    if (trace.temp_rise_c <= 0.0) {
        return std::unexpected(CalcError::InvalidTemperatureRise);
    }
    if (via.drill_diam_mm <= via.plating_thickness_mm * 2.0) {
        return std::unexpected(CalcError::InvalidGeometry);
    }

    // Коефіцієнти емпіричної моделі IPC-2152
    const double k = (trace.layer == LayerType::External) ? 0.048 : 0.024;
    constexpr double b = 0.44;
    constexpr double c = 0.725;

    // Площа перерізу за IPC-2152
    const double area_mils2 = std::pow(trace.current_a / (k * std::pow(trace.temp_rise_c, b)), 1.0 / c);
    const double area_mm2 = area_mils2 / (mils_per_mm * mils_per_mm);

    const double foil_thickness_mm = trace.copper_oz * 0.035;
    const double width_mm = area_mm2 / foil_thickness_mm;

    // Температурна корекція провідності міді
    const double operating_temp_c = trace.ambient_temp_c + trace.temp_rise_c;
    const double rho_operating = copper_rho_20c_ohm_mm * (1.0 + copper_tcr_per_c * (operating_temp_c - 20.0));

    // Опір та втрати на доріжці
    const double r_trace = (rho_operating * trace.length_mm) / area_mm2;
    const double v_drop_trace = trace.current_a * r_trace;
    const double p_loss_trace = trace.current_a * v_drop_trace;

    // Геометрія та опір перехідного отвору
    const double a_via_mm2 = std::numbers::pi * via.plating_thickness_mm * (via.drill_diam_mm - via.plating_thickness_mm);
    const double r_single_via = (rho_operating * via.board_thickness_mm) / a_via_mm2;

    const int n_vias = std::max(1, static_cast<int>(std::ceil(trace.current_a / via.max_current_per_via_a)));
    const double r_via_array = r_single_via / static_cast<double>(n_vias);
    const double v_drop_vias = trace.current_a * r_via_array;

    return PowerRailAnalysis{
        .required_width_mm = width_mm,
        .required_width_mils = width_mm * mils_per_mm,
        .trace_resistance_ohm = r_trace,
        .voltage_drop_trace_v = v_drop_trace,
        .power_loss_trace_w = p_loss_trace,
        .required_via_count = n_vias,
        .via_array_res_ohm = r_via_array,
        .voltage_drop_vias_v = v_drop_vias,
        .total_voltage_drop_v = v_drop_trace + v_drop_vias,
        .total_power_loss_w = p_loss_trace + (trace.current_a * v_drop_vias)
    };
}

} // namespace pcb::power

int main()
{
    using namespace pcb::power;

    const TraceParams trace_cfg{
        .current_a = 15.0,
        .temp_rise_c = 20.0,
        .ambient_temp_c = 25.0,
        .copper_oz = 1.0,
        .layer = LayerType::External,
        .length_mm = 60.0
    };

    const ViaParams via_cfg{
        .drill_diam_mm = 0.3,
        .plating_thickness_mm = 0.025,
        .board_thickness_mm = 1.6,
        .max_current_per_via_a = 1.8
    };

    const auto result = calculate_power_rail(trace_cfg, via_cfg);

    if (result) {
        const auto& r = *result;
        std::cout << "=== Результати розрахунку силової шини PCB (C++20) ===\n";
        std::cout << std::format("Струм: {:.1f} А, Перегрів: {:.1f} °C (T_max = {:.1f} °C)\n",
                                 trace_cfg.current_a, trace_cfg.temp_rise_c,
                                 trace_cfg.ambient_temp_c + trace_cfg.temp_rise_c);
        std::cout << std::format("Необхідна ширина доріжки: {:.2f} мм ({:.1f} mils)\n",
                                 r.required_width_mm, r.required_width_mils);
        std::cout << std::format("Опір доріжки (L = {:.0f} мм): {:.3f} мОм\n",
                                 trace_cfg.length_mm, r.trace_resistance_ohm * 1000.0);
        std::cout << std::format("Падіння напруги на доріжці: {:.2f} мВ, втрати: {:.3f} Вт\n",
                                 r.voltage_drop_trace_v * 1000.0, r.power_loss_trace_w);
        std::cout << std::format("Матриця Stitching Vias: {} шт (R_array = {:.3f} мОм)\n",
                                 r.required_via_count, r.via_array_res_ohm * 1000.0);
        std::cout << std::format("Сумарне падіння напруги: {:.2f} мВ\n",
                                 r.total_voltage_drop_v * 1000.0);
        std::cout << std::format("Сумарна розсіювана потужність: {:.3f} Вт\n",
                                 r.total_power_loss_w);
    } else {
        std::cerr << "Помилка розрахунку параметрів силової шини!\n";
    }

    return 0;
}
