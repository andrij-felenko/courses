/*
 * proj_mounting_stress_calc.cpp — Об'єктно-орієнтоване розрахункове ядро (C++20).
 * Сучасні стандарти типізації, constexpr таблиці та структуровані звіти.
 */

#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <format>
#include <optional>
#include <array>
#include <vector>

namespace pcb::calculator {

// ── Константи матеріалів та безпеки ─────────────────────────────────────────
inline constexpr double Fr4YoungModulusGpa      = 20.0;
inline constexpr double Fr4InPlaneCtePpm        = 15.0;
inline constexpr double Fr4MaxCompressiveMpa    = 250.0;
inline constexpr double Ipc9704SafeMicrostrain  = 500.0;

enum class ChassisMaterial : uint8_t {
    Aluminum6061,
    SteelSpcc,
    Stainless304,
    Brass,
    PolycarbonateAbs,
    Custom
};

struct MaterialProperties {
    std::string_view name;
    double cte_ppm_per_k;
    double young_modulus_gpa;
};

[[nodiscard]] constexpr MaterialProperties get_material_info(ChassisMaterial mat, double custom_cte = 0.0) noexcept {
    switch (mat) {
        case ChassisMaterial::Aluminum6061:
            return {"Алюміній AL6061-T6", 23.2, 69.0};
        case ChassisMaterial::SteelSpcc:
            return {"Листова сталь SPCC", 11.8, 205.0};
        case ChassisMaterial::Stainless304:
            return {"Нержавіюча сталь AISI 304", 16.5, 193.0};
        case ChassisMaterial::Brass:
            return {"Латунь ЛС59-1", 18.5, 105.0};
        case ChassisMaterial::PolycarbonateAbs:
            return {"Пластик PC/ABS", 72.0, 2.4};
        case ChassisMaterial::Custom:
        default:
            return {"Користувацький матеріал", custom_cte, 100.0};
    }
}

// ── Структури параметрів та результатів ─────────────────────────────────────
struct MountingNodeConfig {
    double screw_diameter_nominal_mm{3.0};
    double drill_hole_diameter_mm{3.2};
    double washer_outer_diameter_mm{7.0};
    double nut_friction_factor{0.20};
    double tightening_torque_nm{0.60};
    double pcb_thickness_mm{1.60};
    double span_between_standoffs_mm{75.0};
    double standoff_height_mismatch_mm{0.20};
    ChassisMaterial chassis_material{ChassisMaterial::Aluminum6061};
    double custom_chassis_cte_ppm{23.2};
    double min_operating_temp_c{-40.0};
    double max_operating_temp_c{85.0};
};

struct KeepoutRadii {
    double traces_and_planes_mm{0.0};
    double passives_0603_mm{0.0};
    double mlcc_0805_mm{0.0};
    double mlcc_1206_plus_mm{0.0};
    double tooling_access_mm{0.0};
};

struct CalculationResults {
    double clamp_force_n{0.0};
    double washer_contact_area_mm2{0.0};
    double washer_pressure_mpa{0.0};
    bool is_pressure_acceptable{false};

    double peak_surface_microstrain{0.0};
    double pcb_bending_stress_mpa{0.0};
    double mlcc_0402_safety_margin{0.0};
    double mlcc_0805_safety_margin{0.0};
    double mlcc_1206_safety_margin{0.0};
    bool is_ipc9704_safe{false};

    double delta_cte_ppm{0.0};
    double thermal_axis_displacement_mm{0.0};
    double recommended_slot_length_mm{0.0};

    KeepoutRadii keepouts{};
};

// ── Розрахунковий клас ──────────────────────────────────────────────────────
class MountingStressAnalyzer {
public:
    [[nodiscard]] static std::optional<CalculationResults> analyze(const MountingNodeConfig& cfg) noexcept {
        if (cfg.screw_diameter_nominal_mm <= 0.0 || 
            cfg.washer_outer_diameter_mm <= cfg.drill_hole_diameter_mm ||
            cfg.nut_friction_factor <= 0.0 || 
            cfg.pcb_thickness_mm <= 0.0 || 
            cfg.span_between_standoffs_mm <= 0.0) {
            return std::nullopt;
        }

        CalculationResults res{};

        // 1. Осьова сила F = T / (K * d)
        const double d_screw_m = cfg.screw_diameter_nominal_mm * 1e-3;
        res.clamp_force_n = cfg.tightening_torque_nm / (cfg.nut_friction_factor * d_screw_m);

        // 2. Тиск під шайбою
        res.washer_contact_area_mm2 = (std::numbers::pi / 4.0) * 
            (std::pow(cfg.washer_outer_diameter_mm, 2) - std::pow(cfg.drill_hole_diameter_mm, 2));
        res.washer_pressure_mpa = res.clamp_force_n / res.washer_contact_area_mm2;
        res.is_pressure_acceptable = (res.washer_pressure_mpa <= Fr4MaxCompressiveMpa);

        // 3. Згинальна мікродеформація плати: ε = (6 * t * Δh) / L^2
        const double t_m = cfg.pcb_thickness_mm * 1e-3;
        const double dh_m = cfg.standoff_height_mismatch_mm * 1e-3;
        const double l_m = cfg.span_between_standoffs_mm * 1e-3;

        const double strain_unitless = (6.0 * t_m * dh_m) / std::pow(l_m, 2);
        res.peak_surface_microstrain = strain_unitless * 1e6;
        res.pcb_bending_stress_mpa = strain_unitless * (Fr4YoungModulusGpa * 1e3);

        // 4. Оцінка меж IPC/JEDEC-9704
        const double safe_strain = (res.peak_surface_microstrain > 1e-3) ? res.peak_surface_microstrain : 1e-3;
        res.mlcc_0402_safety_margin = 750.0 / safe_strain;
        res.mlcc_0805_safety_margin = 500.0 / safe_strain;
        res.mlcc_1206_safety_margin = 400.0 / safe_strain;
        res.is_ipc9704_safe = (res.peak_surface_microstrain <= Ipc9704SafeMicrostrain);

        // 5. Теплове розширення
        const auto mat_info = get_material_info(cfg.chassis_material, cfg.custom_chassis_cte_ppm);
        res.delta_cte_ppm = std::abs(mat_info.cte_ppm_per_k - Fr4InPlaneCtePpm);
        const double delta_t = std::abs(cfg.max_operating_temp_c - cfg.min_operating_temp_c);
        res.thermal_axis_displacement_mm = cfg.span_between_standoffs_mm * (res.delta_cte_ppm * 1e-6) * delta_t;
        res.recommended_slot_length_mm = cfg.drill_hole_diameter_mm + res.thermal_axis_displacement_mm + 0.30;

        // 6. Зони заборони
        const double r_wash = cfg.washer_outer_diameter_mm / 2.0;
        res.keepouts.traces_and_planes_mm = r_wash + 0.80;
        res.keepouts.passives_0603_mm     = r_wash + 1.50;
        res.keepouts.mlcc_0805_mm        = r_wash + 2.50;
        res.keepouts.mlcc_1206_plus_mm    = r_wash + 4.00;
        res.keepouts.tooling_access_mm    = r_wash + 4.50;

        return res;
    }

    static void print_formatted_report(const MountingNodeConfig& cfg, const CalculationResults& res) {
        const auto mat = get_material_info(cfg.chassis_material, cfg.custom_chassis_cte_ppm);

        std::cout << "===================================================================\n";
        std::cout << "  ЗВЕДЕНИЙ ЗВІТ РОЗРАХУНКУ КРІПИЛЬНОГО ВУЗЛА ПЛАТИ (C++20 ENGINE)  \n";
        std::cout << "===================================================================\n\n";

        std::cout << "[1] ВХІДНІ ДАНІ КОНСТРУКЦІЇ:\n";
        std::cout << std::format("  • Номінал гвинта:              M{:.1f} (Свердління: Ø{:.2f} мм)\n", cfg.screw_diameter_nominal_mm, cfg.drill_hole_diameter_mm);
        std::cout << std::format("  • Зовнішній діаметр шайби:     Ø{:.2f} мм\n", cfg.washer_outer_diameter_mm);
        std::cout << std::format("  • Момент затягування:          {:.2f} Н·м (Коефіцієнт K = {:.2f})\n", cfg.tightening_torque_nm, cfg.nut_friction_factor);
        std::cout << std::format("  • Друкована плата:             t = {:.2f} мм, Проліт L = {:.1f} мм\n", cfg.pcb_thickness_mm, cfg.span_between_standoffs_mm);
        std::cout << std::format("  • Висотний перекіс стійок:     {:.3f} мм ({:.0f} мкм)\n", cfg.standoff_height_mismatch_mm, cfg.standoff_height_mismatch_mm * 1000.0);
        std::cout << std::format("  • Матеріал шасі:               {} (CTE = {:.1f} ppm/K)\n", mat.name, mat.cte_ppm_per_k);
        std::cout << std::format("  • Робочий діапазон:            {:.1f} °C .. +{:.1f} °C (ΔT = {:.1f} °C)\n\n",
                                 cfg.min_operating_temp_c, cfg.max_operating_temp_c,
                                 std::abs(cfg.max_operating_temp_c - cfg.min_operating_temp_c));

        std::cout << "[2] СИЛОВІ ПАРАМЕТРИ ЗАТЯЖКИ:\n";
        std::cout << std::format("  • Осьове стискання F_clamp:    {:.1f} Н ({:.1f} кгс)\n", res.clamp_force_n, res.clamp_force_n / 9.80665);
        std::cout << std::format("  • Площа контакту шайби:        {:.2f} мм²\n", res.washer_contact_area_mm2);
        std::cout << std::format("  • Контактний тиск на ламінат:  {:.2f} МПа (Ліміт: 250 МПа) -> {}\n\n",
                                 res.washer_pressure_mpa, res.is_pressure_acceptable ? "[НОРМА]" : "[ПЕРЕВИЩЕННЯ]");

        std::cout << "[3] ЗГИНАЛЬНІ ДЕФОРМАЦІЇ ТА ДІАГНОСТИКА IPC-9704:\n";
        std::cout << std::format("  • Пікова поверхнева деформація:{:.1f} με\n", res.peak_surface_microstrain);
        std::cout << std::format("  • Згинальне напруження FR-4:   {:.2f} МПа\n", res.pcb_bending_stress_mpa);
        std::cout << std::format("  • Запас міцності MLCC 0402:    {:.2f} x -> {}\n", res.mlcc_0402_safety_margin, res.mlcc_0402_safety_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
        std::cout << std::format("  • Запас міцності MLCC 0805:    {:.2f} x -> {}\n", res.mlcc_0805_safety_margin, res.mlcc_0805_safety_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
        std::cout << std::format("  • Запас міцності MLCC 1206:    {:.2f} x -> {}\n", res.mlcc_1206_safety_margin, res.mlcc_1206_safety_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
        std::cout << std::format("  • Статус відповідності IPC:    {}\n\n",
                                 res.is_ipc9704_safe ? "✓ БЕЗПЕЧНО (<= 500 με)" : "✖ КРИТИЧНО: ВИСОКИЙ РИЗИК ТРІЩИН MLCC");

        std::cout << "[4] ТЕМПЕРАТУРНА КОМПЕНСАЦІЯ:\n";
        std::cout << std::format("  • Різниця коефіцієнтів |ΔCTE|: {:.1f} ppm/K\n", res.delta_cte_ppm);
        std::cout << std::format("  • Теплове зміщення осей:       {:.3f} мм ({:.1f} мкм)\n", res.thermal_axis_displacement_mm, res.thermal_axis_displacement_mm * 1000.0);
        std::cout << std::format("  • Рекомендований розмір паза:  Ø{:.2f} × {:.2f} мм\n\n", cfg.drill_hole_diameter_mm, res.recommended_slot_length_mm);

        std::cout << "[5] ЗОНИ ВІДЧУЖЕННЯ (KEEPOUT RADIUS):\n";
        std::cout << std::format("  • Мідні доріжки та полігони:   R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.traces_and_planes_mm, res.keepouts.traces_and_planes_mm * 2.0);
        std::cout << std::format("  • Пасиви 0603:                 R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.passives_0603_mm, res.keepouts.passives_0603_mm * 2.0);
        std::cout << std::format("  • Конденсатори MLCC 0805:      R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.mlcc_0805_mm, res.keepouts.mlcc_0805_mm * 2.0);
        std::cout << std::format("  • Конденсатори MLCC 1206+:     R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.mlcc_1206_plus_mm, res.keepouts.mlcc_1206_plus_mm * 2.0);
        std::cout << std::format("  • Інструментальний доступ:     R >= {:.2f} мм (Ø >= {:.2f} мм, Z > 25 мм)\n", res.keepouts.tooling_access_mm, res.keepouts.tooling_access_mm * 2.0);
        std::cout << "===================================================================\n";
    }
};

} // namespace pcb::calculator

int main() {
    using namespace pcb::calculator;

    MountingNodeConfig config{
        .screw_diameter_nominal_mm   = 3.0,
        .drill_hole_diameter_mm      = 3.2,
        .washer_outer_diameter_mm    = 7.0,
        .nut_friction_factor         = 0.20,
        .tightening_torque_nm        = 0.60,
        .pcb_thickness_mm            = 1.60,
        .span_between_standoffs_mm   = 75.0,
        .standoff_height_mismatch_mm = 0.20,
        .chassis_material            = ChassisMaterial::Aluminum6061,
        .custom_chassis_cte_ppm      = 23.2,
        .min_operating_temp_c        = -40.0,
        .max_operating_temp_c        = 85.0
    };

    if (const auto results = MountingStressAnalyzer::analyze(config); results.has_value()) {
        MountingStressAnalyzer::print_formatted_report(config, *results);
    } else {
        std::cerr << "Помилка: недійсні параметри конфігурації кріплення.\n";
        return 1;
    }

    return 0;
}
