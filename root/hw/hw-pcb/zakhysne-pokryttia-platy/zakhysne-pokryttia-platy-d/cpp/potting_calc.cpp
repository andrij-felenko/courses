// potting_calc.cpp — Ідіоматичний C++20 калькулятор параметрів заливки друкованих плат
#include <iostream>
#include <string_view>
#include <vector>
#include <cmath>
#include <iomanip>
#include <expected>
#include <format>

struct MaterialProps {
    std::string_view name;
    double thermal_conductivity{0.2}; // Вт/(м·К)
    double young_modulus_mpa{100.0};   // Модуль Юнга, МПа
    double cte_ppm{60.0};              // КТР, ppm/K (10^-6 1/K)
    double density_g_cm3{1.2};         // Густина, г/см³
    double poisson_ratio{0.38};        // Коефіцієнт Пуассона
};

struct PottingInput {
    double box_length_mm{0.0};
    double box_width_mm{0.0};
    double box_height_mm{0.0};
    double pcb_length_mm{0.0};
    double pcb_width_mm{0.0};
    double pcb_thickness_mm{1.6};
    double components_vol_cm3{0.0};
    double coating_thickness_mm{2.0};  // Товщина шару над чіпом
    double chip_area_mm2{100.0};       // Площа тепловідводу чіпа
    double temp_delta_c{70.0};         // Температурний перепад ΔT (°C)
    double component_cte_ppm{9.0};     // КТР кераміки MLCC або кремнію
};

struct PottingResult {
    double net_volume_cm3{0.0};
    double compound_mass_g{0.0};
    double thermal_resistance_k_w{0.0};
    double cte_stress_mpa{0.0};
    bool is_stress_critical{false};
};

enum class CalcError {
    InvalidDimensions,
    InvalidPhysicalProperties,
    NegativeVolume
};

class PottingAnalyzer {
public:
    [[nodiscard]] static std::expected<PottingResult, CalcError> evaluate(
        const MaterialProps& mat, const PottingInput& in) noexcept 
    {
        if (in.box_length_mm <= 0.0 || in.box_width_mm <= 0.0 || in.box_height_mm <= 0.0 ||
            in.pcb_length_mm <= 0.0 || in.pcb_width_mm <= 0.0 || in.chip_area_mm2 <= 0.0) {
            return std::unexpected(CalcError::InvalidDimensions);
        }
        if (mat.thermal_conductivity <= 0.0 || mat.density_g_cm3 <= 0.0 || mat.poisson_ratio >= 0.5) {
            return std::unexpected(CalcError::InvalidPhysicalProperties);
        }

        PottingResult res;
        
        // 1. Обчислення вільного об'єму під заливку
        const double box_vol = (in.box_length_mm * in.box_width_mm * in.box_height_mm) / 1000.0;
        const double pcb_vol = (in.pcb_length_mm * in.pcb_width_mm * in.pcb_thickness_mm) / 1000.0;
        res.net_volume_cm3 = box_vol - pcb_vol - in.components_vol_cm3;
        if (res.net_volume_cm3 < 0.0) {
            return std::unexpected(CalcError::NegativeVolume);
        }
        res.compound_mass_g = res.net_volume_cm3 * mat.density_g_cm3;

        // 2. Тепловий опір шару компаунда: R_th = t / (k * A)
        const double t_m = in.coating_thickness_mm / 1000.0;
        const double a_m2 = in.chip_area_mm2 / 1'000'000.0;
        res.thermal_resistance_k_w = t_m / (mat.thermal_conductivity * a_m2);

        // 3. Термомеханічні напруження від КТР: σ = E * |Δα| * ΔT / (1 - ν)
        const double delta_cte = std::abs(mat.cte_ppm - in.component_cte_ppm) * 1e-6;
        const double denom = 1.0 - mat.poisson_ratio;
        res.cte_stress_mpa = (mat.young_modulus_mpa * delta_cte * in.temp_delta_c) / denom;
        
        // Критичний поріг міцності кераміки конденсаторів (типово 40-50 МПа)
        res.is_stress_critical = (res.cte_stress_mpa > 40.0);

        return res;
    }
};

int main() {
    const std::vector<MaterialProps> materials = {
        {"PU-T1 (Теплопровідний поліуретан)", 0.95, 80.0, 70.0, 1.75, 0.38},
        {"EP-R1 (Жорсткий епоксидний компаунд)", 0.75, 3200.0, 35.0, 1.85, 0.35},
        {"SI-T1 (Теплопровідний силікон)", 1.50, 15.0, 180.0, 2.35, 0.45}
    };

    constexpr PottingInput input{
        .box_length_mm = 80.0,
        .box_width_mm = 60.0,
        .box_height_mm = 20.0,
        .pcb_length_mm = 75.0,
        .pcb_width_mm = 55.0,
        .pcb_thickness_mm = 1.6,
        .components_vol_cm3 = 8.5,
        .coating_thickness_mm = 3.0,
        .chip_area_mm2 = 144.0,       // QFN чіп 12x12 мм
        .temp_delta_c = 85.0,         // ΔT = 85 °C
        .component_cte_ppm = 9.0      // MLCC кераміка
    };

    std::cout << "=== ІНЖЕНЕРНИЙ АНАЛІЗ МАТЕРІАЛІВ ЗАЛИВКИ (C++20) ===\n";
    std::cout << std::format("Корпус: {:.1f}x{:.1f}x{:.1f} мм | Чіп: {:.1f} мм² | Шар: {:.1f} мм | ΔT: {:.1f} °C\n\n",
                             input.box_length_mm, input.box_width_mm, input.box_height_mm,
                             input.chip_area_mm2, input.coating_thickness_mm, input.temp_delta_c);

    for (const auto& mat : materials) {
        auto result = PottingAnalyzer::evaluate(mat, input);
        if (result) {
            std::cout << std::format("Матеріал: {}\n", mat.name);
            std::cout << std::format("  - Об'єм смоли       : {:.2f} см³\n", result->net_volume_cm3);
            std::cout << std::format("  - Маса компаунда    : {:.2f} г\n", result->compound_mass_g);
            std::cout << std::format("  - Тепловий опір R_th: {:.2f} K/Вт\n", result->thermal_resistance_k_w);
            std::cout << std::format("  - Напруження σ (CTE): {:.2f} МПа {}\n",
                                     result->cte_stress_mpa,
                                     result->is_stress_critical ? "[КРИТИЧНО: РИЗИК СКОЛУ MLCC]" : "[НОРМА]");
            std::cout << "------------------------------------------------------------\n";
        } else {
            std::cerr << "Помилка розрахунку для матеріалу: " << mat.name << '\n';
        }
    }
    return 0;
}
