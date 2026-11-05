#pragma once

#include "pcb_layer.hpp"
#include <vector>
#include <string>

/**
 * @brief Інженерний калькулятор для тривимірного моделювання та валідації стеків друкованих плат.
 */
class StackAssemblyCalculator {
public:
    /**
     * @brief Результати аналізу окремого міжплатного ярусу.
     */
    struct TierAnalysisResult {
        std::string lower_layer_name;
        std::string upper_layer_name;
        double standoff_height_mm{0.0};
        double component_envelope_mm{0.0};    ///< Сума висот зустрічних компонентів і пайки
        double actual_clearance_mm{0.0};      ///< Залишковий зазор між найближчими точками
        double safe_clearance_margin_mm{0.0}; ///< Запас дотик/замикання з урахуванням прогину
        bool collision_risk{false};           ///< Ознака механічного торкання або колізії
        double recommended_torque_nm{0.0};    ///< Рекомендований момент затягування (Н*м)
        double max_allowable_torque_nm{0.0};  ///< Граничний крутний момент до зриву нарізі (Н*м)
    };

    /**
     * @brief Зведений підсумковий звіт за всім стеком приладу.
     */
    struct StackReport {
        std::vector<TierAnalysisResult> tiers;
        double total_stack_height_mm{0.0};
        bool has_collisions{false};
    };

    StackAssemblyCalculator() = default;

    /**
     * @brief Задає нижню базову плату стека.
     */
    void setBaseBoard(PcbLayer base_layer);

    /**
     * @brief Додає наступний верхній ярус плати разом із параметрами дистанційних стійок під ним.
     */
    void addStackedBoard(PcbLayer upper_layer, StandoffTierConfig tier_config);

    /**
     * @brief Виконує повний інженерний аналіз геометрії, зазорів та моментів затягування.
     */
    [[nodiscard]] StackReport analyzeStack() const;

    /**
     * @brief Виводить у консоль докладний інженерний звіт про безпеку компонування.
     */
    void printReport(const StackReport& report) const;

    /**
     * @brief Перевіряє, чи безпечний заданий крутний момент для монтажу конкретного типу стійки.
     */
    [[nodiscard]] static bool isTorqueSafe(StandoffThread thread, StandoffMaterial material, double torque_nm) noexcept;

private:
    struct StackNode {
        PcbLayer layer;
        StandoffTierConfig standoff_to_next;
    };

    std::vector<PcbLayer> layers_;
    std::vector<StandoffTierConfig> tiers_;
};
