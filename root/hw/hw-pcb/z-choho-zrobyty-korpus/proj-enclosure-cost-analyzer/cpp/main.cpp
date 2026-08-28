#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <format>
#include <optional>
#include <cmath>
#include <algorithm>
#include <numbers>

namespace EnclosureCost {

struct MaterialProperties {
    std::string_view name;
    double density_g_cm3;
    double cost_per_kg_usd;
    double thermal_conductivity_w_mk;
    double max_continuous_temp_c;
};

inline constexpr MaterialProperties MAT_PETG   { "PETG",          1.27, 24.0, 0.20,  70.0 };
inline constexpr MaterialProperties MAT_ABS    { "ABS",           1.05, 22.0, 0.18,  90.0 };
inline constexpr MaterialProperties MAT_PA12   { "PA12 (Nylon)",  1.01, 65.0, 0.25, 120.0 };
inline constexpr MaterialProperties MAT_AL6061 { "Al 6061-T6",    2.70,  8.5, 167.0, 200.0 };

enum class ManufacturingTechnology {
    Fdm3DPrinting,
    MjfPa12Printing,
    CncMillingAl6061,
    OffTheShelfModified,
    InjectionMolding
};

struct EnclosureDesign {
    double length_mm{ 120.0 };
    double width_mm{ 80.0 };
    double height_mm{ 35.0 };
    double wall_thickness_mm{ 2.5 };
    int num_port_cutouts{ 4 };
    int num_threaded_inserts{ 4 };
    int num_side_sliders{ 1 };
    double thermal_load_watts{ 5.0 };
    bool require_ip67{ true };

    [[nodiscard]] constexpr double surface_area_cm2() const noexcept {
        double l_cm = length_mm / 10.0;
        double w_cm = width_mm / 10.0;
        double h_cm = height_mm / 10.0;
        return 2.0 * (l_cm * w_cm + l_cm * h_cm + w_cm * h_cm);
    }

    [[nodiscard]] constexpr double net_volume_cm3() const noexcept {
        double l_cm = length_mm / 10.0;
        double w_cm = width_mm / 10.0;
        double h_cm = height_mm / 10.0;
        double t_cm = wall_thickness_mm / 10.0;

        double v_ext = l_cm * w_cm * h_cm;
        double v_int = std::max(0.0, (l_cm - 2.0 * t_cm) * (w_cm - 2.0 * t_cm) * (h_cm - 2.0 * t_cm));
        return v_ext - v_int;
    }
};

struct CostBreakdown {
    ManufacturingTechnology tech;
    std::string_view tech_name;
    double nre_tooling_cost_usd{ 0.0 };
    double batch_setup_cost_usd{ 0.0 };
    double unit_raw_material_usd{ 0.0 };
    double unit_machining_usd{ 0.0 };
    double unit_post_process_usd{ 0.0 };
    double unit_labor_usd{ 0.0 };
    bool is_feasible{ true };
    std::string feasibility_note{ "OK" };

    [[nodiscard]] constexpr double unit_production_cost() const noexcept {
        return unit_raw_material_usd + unit_machining_usd + unit_post_process_usd + unit_labor_usd;
    }

    [[nodiscard]] double total_unit_cost(int batch_size) const noexcept {
        if (batch_size <= 0) return 0.0;
        double amortized_nre = nre_tooling_cost_usd / static_cast<double>(batch_size);
        double amortized_setup = batch_setup_cost_usd / static_cast<double>(batch_size);
        return amortized_nre + amortized_setup + unit_production_cost();
    }
};

class CostEstimator {
public:
    static CostBreakdown evaluate_fdm(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::Fdm3DPrinting,
            .tech_name = "3D-друк FDM (PETG/ABS)"
        };

        double v_net = design.net_volume_cm3();
        double mass_g = v_net * MAT_PETG.density_g_cm3;
        cb.unit_raw_material_usd = (mass_g / 1000.0) * MAT_PETG.cost_per_kg_usd;

        double print_hours = std::max(0.5, v_net / 12.0); // 12 см3/год
        cb.unit_machining_usd = print_hours * 4.50; // 4.50 USD/год машинного часу
        cb.unit_post_process_usd = design.num_threaded_inserts * 0.25;
        cb.unit_labor_usd = (0.10 + design.num_threaded_inserts * 0.02) * 25.0;

        cb.nre_tooling_cost_usd = 0.0;
        cb.batch_setup_cost_usd = 10.0;

        if (design.thermal_load_watts > 8.0) {
            cb.is_feasible = false;
            cb.feasibility_note = std::format("Теплове навантаження {:.1f} Вт перевищує ліміт пластику", design.thermal_load_watts);
        } else if (design.require_ip67) {
            cb.is_feasible = false;
            cb.feasibility_note = "Мікропористість шарів FDM не забезпечує IP67";
        }
        return cb;
    }

    static CostBreakdown evaluate_mjf(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::MjfPa12Printing,
            .tech_name = "3D-друк MJF (PA12 Nylon)"
        };

        double v_net = design.net_volume_cm3();
        cb.unit_raw_material_usd = v_net * 0.35; // 0.35 USD/см3 з урахуванням порошку
        cb.unit_machining_usd = 5.00;
        cb.unit_post_process_usd = (design.require_ip67 ? 6.50 : 2.00) + design.num_threaded_inserts * 0.25;
        cb.unit_labor_usd = 0.08 * 25.0;

        cb.nre_tooling_cost_usd = 0.0;
        cb.batch_setup_cost_usd = 35.0;

        if (design.thermal_load_watts > 12.0) {
            cb.is_feasible = false;
            cb.feasibility_note = std::format("Низька теплопровідність PA12 для {:.1f} Вт", design.thermal_load_watts);
        } else {
            cb.feasibility_note = design.require_ip67 ? "Потрібне парове згладжування для IP67" : "Повністю ізотропний корпус";
        }
        return cb;
    }

    static CostBreakdown evaluate_cnc_aluminum(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::CncMillingAl6061,
            .tech_name = "ЧПУ фрезерування (Al 6061-T6)"
        };

        double stock_l_cm = (design.length_mm + 10.0) / 10.0;
        double stock_w_cm = (design.width_mm + 10.0) / 10.0;
        double stock_h_cm = (design.height_mm + 6.0) / 10.0;
        double v_stock = stock_l_cm * stock_w_cm * stock_h_cm;
        double v_net = design.net_volume_cm3();
        double s_area = design.surface_area_cm2();

        double mass_stock_kg = (v_stock * MAT_AL6061.density_g_cm3) / 1000.0;
        cb.unit_raw_material_usd = mass_stock_kg * MAT_AL6061.cost_per_kg_usd;

        double v_removed = v_stock - v_net;
        double mrr = 75.0; // 75 см3/хв
        double t_mach_min = (v_removed / mrr) + (s_area * 0.05) + (design.num_port_cutouts * 2.5) + 8.0;

        cb.unit_machining_usd = (t_mach_min / 60.0) * 55.0; // 55 USD/год ЧПУ
        double area_dm2 = s_area / 100.0;
        cb.unit_post_process_usd = std::max(4.0, area_dm2 * 20.0); // Анодування Type II
        cb.unit_labor_usd = 0.10 * 25.0;

        cb.nre_tooling_cost_usd = 180.0; // CAM програмування
        cb.batch_setup_cost_usd = 60.0;

        cb.feasibility_note = "Виняткове тепловідведення (167 Вт/(м·К)) та ЕМС захист";
        return cb;
    }

    static CostBreakdown evaluate_off_shelf(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::OffTheShelfModified,
            .tech_name = "Готовий корпус з доробкою"
        };

        double volume_liters = (design.length_mm * design.width_mm * design.height_mm) / 1e6;
        double catalog_base = 6.0 + (volume_liters * 18.0) + (design.require_ip67 ? 4.50 : 0.0);

        cb.unit_raw_material_usd = catalog_base;
        double t_mod_min = (design.num_port_cutouts * 1.5) + 3.0;
        cb.unit_machining_usd = (t_mod_min / 60.0) * 55.0;
        cb.unit_post_process_usd = 1.50; // Лазерне маркування
        cb.unit_labor_usd = 0.05 * 25.0;

        cb.nre_tooling_cost_usd = 50.0;
        cb.batch_setup_cost_usd = 25.0;

        if (design.thermal_load_watts > 25.0) {
            cb.is_feasible = false;
            cb.feasibility_note = "Потрібний додатковий зовнішній радіатор";
        } else {
            cb.feasibility_note = "Швидкий вихід на ринок для малих партій";
        }
        return cb;
    }

    static CostBreakdown evaluate_injection_molding(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::InjectionMolding,
            .tech_name = "Лиття під тиском (Injection)"
        };

        double v_net = design.net_volume_cm3();
        double mass_g = v_net * MAT_ABS.density_g_cm3;
        cb.unit_raw_material_usd = (mass_g / 1000.0) * 3.20 * 1.15; // ABS гранули + 15% ливники

        double cycle_sec = 12.0 + (design.wall_thickness_mm * design.wall_thickness_mm * 2.5);
        cb.unit_machining_usd = (cycle_sec / 3600.0) * 45.0;
        cb.unit_post_process_usd = design.num_threaded_inserts * 0.15;
        cb.unit_labor_usd = (cycle_sec / 3600.0) * 25.0 * 0.3;

        double mold_nre = 10000.0 + (design.surface_area_cm2() * 12.0);
        if (design.num_side_sliders > 0) {
            mold_nre += design.num_side_sliders * 2200.0;
        }
        cb.nre_tooling_cost_usd = mold_nre;
        cb.batch_setup_cost_usd = 250.0;

        if (design.thermal_load_watts > 10.0) {
            cb.is_feasible = false;
            cb.feasibility_note = "Пластик вимагає металевих теплових вставок";
        } else {
            cb.feasibility_note = "Найнижча собівартість при тиражі від 1 500 шт";
        }
        return cb;
    }
};

} // namespace EnclosureCost

int main() {
    using namespace EnclosureCost;

    EnclosureDesign specs{
        .length_mm = 120.0,
        .width_mm = 80.0,
        .height_mm = 35.0,
        .wall_thickness_mm = 2.5,
        .num_port_cutouts = 4,
        .num_threaded_inserts = 4,
        .num_side_sliders = 1,
        .thermal_load_watts = 5.0,
        .require_ip67 = true
    };

    std::cout << "================================================================================\n";
    std::cout << "     АНАЛІЗАТОР СОБІВАРТОСТІ ТА ВИБОРУ ТЕХНОЛОГІЇ ВИГОТОВЛЕННЯ КОРПУСУ\n";
    std::cout << "================================================================================\n";
    std::cout << std::format("Параметри корпусу: {:.1f} x {:.1f} x {:.1f} мм, стінка {:.1f} мм\n",
                             specs.length_mm, specs.width_mm, specs.height_mm, specs.wall_thickness_mm);
    std::cout << std::format("Вимоги: Вирізів: {}, Вставок: {}, Тепло: {:.1f} Вт, IP67: {}\n\n",
                             specs.num_port_cutouts, specs.num_threaded_inserts, specs.thermal_load_watts,
                             specs.require_ip67 ? "ТАК" : "НІ");

    std::vector<CostBreakdown> breakdowns = {
        CostEstimator::evaluate_fdm(specs),
        CostEstimator::evaluate_mjf(specs),
        CostEstimator::evaluate_cnc_aluminum(specs),
        CostEstimator::evaluate_off_shelf(specs),
        CostEstimator::evaluate_injection_molding(specs)
    };

    std::cout << "--------------------------------------------------------------------------------\n";
    std::cout << std::format("{:<30} | {:<8} | {:<8} | {:<8} | {:<8}\n",
                             "Технологічний процес", "NRE ($)", "Raw ($)", "Mach ($)", "Feasible?");
    std::cout << "--------------------------------------------------------------------------------\n";

    for (const auto& b : breakdowns) {
        std::cout << std::format("{:<30} | {:8.1f} | {:8.2f} | {:8.2f} | {:<8}\n",
                                 b.tech_name, b.nre_tooling_cost_usd, b.unit_raw_material_usd,
                                 b.unit_machining_usd, b.is_feasible ? "ТАК" : "НІ");
    }
    std::cout << "--------------------------------------------------------------------------------\n\n";

    const std::vector<int> batches = { 1, 10, 50, 100, 500, 1000, 5000, 20000 };

    std::cout << "ПОРІВНЯЛЬНА ТАБЛИЦЯ ПИТОМОЇ СОБІВАРТОСТІ 1 КОРПУСУ (USD / шт):\n";
    std::cout << "--------------------------------------------------------------------------------\n";
    std::cout << std::format("{:<26}", "Тираж партії (шт):");
    for (int count : batches) {
        std::cout << std::format(" | {:6d}", count);
    }
    std::cout << "\n--------------------------------------------------------------------------------\n";

    for (const auto& b : breakdowns) {
        std::cout << std::format("{:<26}", b.tech_name);
        for (int count : batches) {
            if (!b.is_feasible) {
                std::cout << " |   N/A ";
            } else {
                double cost = b.total_unit_cost(count);
                if (cost > 999.0) {
                    std::cout << " | >$999 ";
                } else {
                    std::cout << std::format(" | {:6.2f}", cost);
                }
            }
        }
        std::cout << "\n";
    }
    std::cout << "--------------------------------------------------------------------------------\n\n";

    std::cout << "РЕКОМЕНДАЦІЇ ТЕХНОЛОГІЧНОГО МАРШРУТУ ЗА РОЗМІРОМ ПАРТІЇ:\n";
    for (int count : batches) {
        std::optional<CostBreakdown> best;
        double min_cost = 1e9;

        for (const auto& b : breakdowns) {
            if (!b.is_feasible) continue;
            double cost = b.total_unit_cost(count);
            if (cost < min_cost) {
                min_cost = cost;
                best = b;
            }
        }

        if (best.has_value()) {
            std::cout << std::format("  Тираж {:5d} шт: -> {:<30} (${:.2f} / шт)\n",
                                     count, best->tech_name, min_cost);
        } else {
            std::cout << std::format("  Тираж {:5d} шт: -> Жодна технологія не задовольняє вимоги\n", count);
        }
    }
    std::cout << "================================================================================\n";

    return 0;
}
