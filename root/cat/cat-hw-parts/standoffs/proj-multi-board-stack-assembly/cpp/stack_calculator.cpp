#include "stack_calculator.hpp"
#include <iostream>
#include <iomanip>

namespace {
    void getTorqueValues(StandoffThread thread, StandoffMaterial material, double& rec_t, double& max_t) {
        if (thread == StandoffThread::M2) {
            if (material == StandoffMaterial::BrassCW614N) {
                rec_t = 0.22;
                max_t = 0.28;
            } else {
                rec_t = 0.07;
                max_t = 0.09;
            }
        } else { // StandoffThread::M3
            if (material == StandoffMaterial::BrassCW614N) {
                rec_t = 0.58;
                max_t = 0.70;
            } else {
                rec_t = 0.18;
                max_t = 0.24;
            }
        }
    }
}

void StackAssemblyCalculator::setBaseBoard(PcbLayer base_layer) {
    layers_.clear();
    tiers_.clear();
    layers_.push_back(std::move(base_layer));
}

void StackAssemblyCalculator::addStackedBoard(PcbLayer upper_layer, StandoffTierConfig tier_config) {
    tiers_.push_back(tier_config);
    layers_.push_back(std::move(upper_layer));
}

bool StackAssemblyCalculator::isTorqueSafe(StandoffThread thread, StandoffMaterial material, double torque_nm) noexcept {
    double rec_t = 0.0, max_t = 0.0;
    getTorqueValues(thread, material, rec_t, max_t);
    return (torque_nm <= max_t);
}

StackAssemblyCalculator::StackReport StackAssemblyCalculator::analyzeStack() const {
    StackReport report{};
    if (layers_.empty()) return report;

    double cumulative_height = layers_[0].pcb_thickness_mm;

    for (size_t i = 0; i < tiers_.size(); ++i) {
        const auto& lower = layers_[i];
        const auto& upper = layers_[i + 1];
        const auto& tier = tiers_[i];

        TierAnalysisResult res{};
        res.lower_layer_name = lower.name;
        res.upper_layer_name = upper.name;
        res.standoff_height_mm = tier.standoff_height_mm;

        // Висота зустрічних об'ємів: деталі на верхній площині нижньої плати +
        // SMD деталі або хвостики виводів на нижній площині верхньої плати
        double bottom_envelope = upper.bottom_components_height_mm + upper.bottom_leads_protrusion_mm;
        res.component_envelope_mm = lower.top_components_height_mm + bottom_envelope;

        // Фактичний залишковий зазор між деталями
        res.actual_clearance_mm = tier.standoff_height_mm - res.component_envelope_mm;

        // Запас надійності з урахуванням прогину обох плат
        double combined_deflection = lower.max_deflection_mm + upper.max_deflection_mm;
        res.safe_clearance_margin_mm = res.actual_clearance_mm - combined_deflection;

        // Колізія виникає, якщо запас менший за необхідний повітряний зазор
        res.collision_risk = (res.safe_clearance_margin_mm < tier.required_air_gap_mm);
        if (res.collision_risk) {
            report.has_collisions = true;
        }

        getTorqueValues(tier.thread, tier.material, res.recommended_torque_nm, res.max_allowable_torque_nm);

        report.tiers.push_back(res);

        cumulative_height += tier.standoff_height_mm + upper.pcb_thickness_mm;
    }

    report.total_stack_height_mm = cumulative_height;
    return report;
}

void StackAssemblyCalculator::printReport(const StackReport& report) const {
    std::cout << "\n==============================================================================\n";
    std::cout << "          ІНЖЕНЕРНИЙ ЗВІТ КОМПОНУВАННЯ БАГАТОПЛАТНОГО СТЕКА (C++17)          \n";
    std::cout << "==============================================================================\n";

    for (size_t i = 0; i < report.tiers.size(); ++i) {
        const auto& t = report.tiers[i];
        std::cout << "ЯРУС " << (i + 1) << ": [" << t.lower_layer_name << "] ---> [" << t.upper_layer_name << "]\n";
        std::cout << "  Висота стійок (H_s)          : " << std::fixed << std::setprecision(2) 
                  << t.standoff_height_mm << " мм\n";
        std::cout << "  Сумарний виліт компонентів   : " << t.component_envelope_mm << " мм\n";
        std::cout << "  Фактичний зазор деталей      : " << t.actual_clearance_mm << " мм\n";
        std::cout << "  Запас безпеки (з прогином)   : " << t.safe_clearance_margin_mm << " мм\n";
        std::cout << "  Регламентний момент затягу   : " << t.recommended_torque_nm 
                  << " Н*м (граничний: " << t.max_allowable_torque_nm << " Н*м)\n";

        if (t.collision_risk) {
            std::cout << "  СТАТУС: [ПОМИЛКА! НЕБЕЗПЕКА КОЛІЗІЇ / ЗАМИКАННЯ]\n";
            std::cout << "  ПОРАДА: Збільшити висоту стійки або змінити висоту електролітів/роз'ємів!\n";
        } else {
            std::cout << "  СТАТУС: [ВЕРДИКТ: БЕЗПЕЧНО] Норматив зазору витримано.\n";
        }
        std::cout << "------------------------------------------------------------------------------\n";
    }

    std::cout << "Загальна конструктивна висота стека плат: " 
              << std::fixed << std::setprecision(2) << report.total_stack_height_mm << " мм\n";
    std::cout << "Загальний висновок надійності: " 
              << (report.has_collisions ? "[ПОТРІБНЕ ДООПРАЦЮВАННЯ]" : "[ГОТОВО ДО ВИРОБНИЦТВА]") << "\n";
    std::cout << "==============================================================================\n";
}
