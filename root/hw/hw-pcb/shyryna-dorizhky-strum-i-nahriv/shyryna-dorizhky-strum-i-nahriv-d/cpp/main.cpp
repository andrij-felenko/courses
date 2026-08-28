#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>

namespace pcb::thermal {

struct TraceInput {
    double current_amps{15.0};
    double temp_rise_c{20.0};
    double ambient_temp_c{25.0};
    double copper_thickness_oz{1.0};
    double trace_length_mm{100.0};
    bool   is_internal{false};
    bool   has_ground_plane{true};
};

struct TraceResult {
    double width_ipc2221_mm{0.0};
    double width_ipc2152_mm{0.0};
    double area_mm2{0.0};
    double resistance_cold_mohm{0.0};
    double resistance_hot_mohm{0.0};
    double voltage_drop_mv{0.0};
    double power_loss_watts{0.0};
    int    min_vias_03mm{1};
};

class TraceCalculator {
public:
    static constexpr double RHO_CU_20C = 1.7241e-8; // Ом·м
    static constexpr double ALPHA_CU   = 0.00393;    // 1/K
    static constexpr double MIL_TO_MM  = 0.0254;

    [[nodiscard]] static constexpr TraceResult calculate(const TraceInput& in) noexcept {
        TraceResult res{};
        const double t_mils = in.copper_thickness_oz * 1.378;
        const double t_mm   = in.copper_thickness_oz * 0.035;

        // 1. Модель IPC-2221A
        const double k = in.is_internal ? 0.024 : 0.048;
        constexpr double b = 0.44;
        constexpr double c = 0.725;

        const double area_mils2 = std::pow(in.current_amps / (k * std::pow(in.temp_rise_c, b)), 1.0 / c);
        res.width_ipc2221_mm = (area_mils2 / t_mils) * MIL_TO_MM;

        // 2. Модель IPC-2152
        const double m_plane = in.has_ground_plane ? 1.35 : 1.00;
        constexpr double m_thick = 1.00;
        const double m_cu = (in.copper_thickness_oz <= 1.0) ? 1.08 : 1.00;
        const double total_derating = m_plane * m_thick * m_cu;

        double area_2152_mils2 = area_mils2 / std::pow(total_derating, 1.0 / c);
        if (in.is_internal && in.has_ground_plane) {
            area_2152_mils2 *= 0.65;
        }
        res.width_ipc2152_mm = (area_2152_mils2 / t_mils) * MIL_TO_MM;

        // Електричні параметри
        res.area_mm2 = res.width_ipc2152_mm * t_mm;
        const double length_m = in.trace_length_mm * 1e-3;
        const double area_m2   = res.area_mm2 * 1e-6;

        const double r_cold = RHO_CU_20C * (length_m / area_m2);
        const double t_hot  = in.ambient_temp_c + in.temp_rise_c;
        const double r_hot  = r_cold * (1.0 + ALPHA_CU * (t_hot - 20.0));

        res.resistance_cold_mohm = r_cold * 1e3;
        res.resistance_hot_mohm  = r_hot * 1e3;
        res.voltage_drop_mv      = in.current_amps * res.resistance_hot_mohm;
        res.power_loss_watts     = in.current_amps * in.current_amps * r_hot;

        res.min_vias_03mm = static_cast<int>(std::ceil(in.current_amps / 1.5));
        if (res.min_vias_03mm < 1) res.min_vias_03mm = 1;

        return res;
    }
};

} // namespace pcb::thermal

int main() {
    using namespace pcb::thermal;

    constexpr TraceInput config{
        .current_amps = 15.0,
        .temp_rise_c = 20.0,
        .ambient_temp_c = 25.0,
        .copper_thickness_oz = 1.0,
        .trace_length_mm = 100.0,
        .is_internal = false,
        .has_ground_plane = true
    };

    const auto res = TraceCalculator::calculate(config);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Розрахунок силового провідника (C++20) ===\n";
    std::cout << "Струм: " << config.current_amps << " A | Перегрів: " << config.temp_rise_c << " °C\n";
    std::cout << "Ширина за IPC-2221: " << res.width_ipc2221_mm << " мм\n";
    std::cout << "Ширина за IPC-2152: " << res.width_ipc2152_mm << " мм\n";
    std::cout << "Гарячий опір: " << res.resistance_hot_mohm << " мОм\n";
    std::cout << "Падіння напруги: " << res.voltage_drop_mv << " мВ\n";
    std::cout << "Втрати потужності: " << res.power_loss_watts << " Вт\n";
    std::cout << "Кількість перехідних отворів (0.3 мм): " << res.min_vias_03mm << " шт\n";

    return 0;
}
