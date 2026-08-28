#ifndef PCB_CURRENT_CALCULATOR_HPP
#define PCB_CURRENT_CALCULATOR_HPP

#include <cmath>
#include <stdexcept>
#include <string>

namespace pcb::design {

enum class LayerLocation {
    Outer, // Зовнішній шар (k = 0.048)
    Inner  // Внутрішній шар (k = 0.024)
};

struct TraceDesignInput {
    double target_current_a{1.0};       // Струм навантаження [А]
    double allowed_temp_rise_c{10.0};   // Допустимий перегрів ΔT [°C]
    double copper_thickness_um{35.0};   // Товщина мідної фольги [мкм]
    LayerLocation layer{LayerLocation::Outer}; // Тип шару
};

struct TraceDesignOutput {
    double min_width_mm{0.0};           // Мінімально допустима ширина доріжки [мм]
    double cross_section_mm2{0.0};      // Площа поперечного перерізу [мм²]
    double current_density_a_mm2{0.0};  // Ефективна щільність струму J [А/мм²]
    double trace_resistance_ohm_m{0.0}; // Опір на один метр довжини [Ом/м]
    double power_loss_w_m{0.0};         // Теплові втрати на метр довжини [Вт/м]
};

class PcbCurrentCalculator {
public:
    static constexpr double COPPER_RESISTIVITY_20C = 1.724e-8; // Ом·м (питомий опір міді)
    static constexpr double COPPER_TEMP_COEFF = 0.00393;       // 1/°C (ТКО міді)

    static TraceDesignOutput calculate_trace_width(const TraceDesignInput& input) {
        if (input.target_current_a <= 0.0) {
            throw std::invalid_argument("Струм повинен бути більшим за нуль.");
        }
        if (input.allowed_temp_rise_c <= 0.0) {
            throw std::invalid_argument("Перегрів повинен бути більшим за нуль.");
        }

        const double k = (input.layer == LayerLocation::Outer) ? 0.048 : 0.024;
        
        // Розрахунок площі A у mil² за формулою IPC-2221
        const double temp_factor = std::pow(input.allowed_temp_rise_c, 0.44);
        const double area_mil2 = std::pow(input.target_current_a / (k * temp_factor), 1.0 / 0.725);

        // Переведення площі у мм² (1 mil² = 6.4516e-4 мм²)
        const double area_mm2 = area_mil2 * 6.4516e-4;

        // Товщина міді у мм
        const double thickness_mm = input.copper_thickness_um / 1000.0;
        const double width_mm = area_mm2 / thickness_mm;

        // Ефективна щільність струму J
        const double density_a_mm2 = input.target_current_a / area_mm2;

        // Опір з урахуванням температури (20 °C + ΔT)
        const double temp_c = 20.0 + input.allowed_temp_rise_c;
        const double rho_actual = COPPER_RESISTIVITY_20C * (1.0 + COPPER_TEMP_COEFF * (temp_c - 20.0));
        const double resistance_per_m = rho_actual / (area_mm2 * 1e-6);

        // Теплова потужність втрат P = I² · R
        const double power_loss_per_m = std::pow(input.target_current_a, 2) * resistance_per_m;

        return TraceDesignOutput{
            width_mm,
            area_mm2,
            density_a_mm2,
            resistance_per_m,
            power_loss_per_m
        };
    }
};

} // namespace pcb::design

#endif // PCB_CURRENT_CALCULATOR_HPP
