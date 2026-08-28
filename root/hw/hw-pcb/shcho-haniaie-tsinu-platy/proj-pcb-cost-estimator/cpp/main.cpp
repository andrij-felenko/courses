#include <iostream>
#include <cmath>
#include <algorithm>
#include <string_view>
#include <span>
#include <expected>
#include <format>
#include <numbers>

namespace pcb_cost {

inline constexpr double PanelWidthMm    = 457.0; // 18 дюймів
inline constexpr double PanelHeightMm   = 610.0; // 24 дюйми
inline constexpr double PanelMarginMm   = 12.5;  // Технологічні поля
inline constexpr double RouterGapMm     = 2.0;   // Зазор на фрезерування
inline constexpr double BaseFr4CostSqm  = 35.0;  // Базовий тариф склотекстоліту
inline constexpr double BaseNreSetup    = 120.0; // Інженерна підготовка виробництва

enum class SurfaceFinish : uint8_t {
    HaslLeadFree,
    Osp,
    Enig,
    Enepig
};

enum class TgRating : uint8_t {
    Standard130,
    Mid150,
    High170
};

enum class CalculatorError : uint8_t {
    InvalidDimensions,
    InvalidQuantity,
    ZeroFitOnPanel
};

struct BoardDimensions {
    double width_mm{0.0};
    double height_mm{0.0};

    [[nodiscard]] constexpr double area_sqm() const noexcept {
        return (width_mm * height_mm) / 1'000'000.0;
    }

    [[nodiscard]] constexpr double area_cm2() const noexcept {
        return (width_mm * height_mm) / 100.0;
    }
};

struct PcbSpecification {
    BoardDimensions dimensions;
    int layer_count{2};
    double copper_oz{1.0};
    double min_trace_mil{6.0};
    double min_space_mil{6.0};
    TgRating tg{TgRating::Standard130};
    SurfaceFinish finish{SurfaceFinish::HaslLeadFree};
    bool has_blind_buried_vias{false};
    bool has_vippo{false};
    int vippo_holes_count{0};
    int order_quantity{100};
    int turnaround_hours{120};
};

struct PcbCostBreakdown {
    int boards_per_panel{0};
    int panels_needed{0};
    double panel_utilization_pct{0.0};
    double estimated_yield{0.0};
    double nre_tooling_cost{0.0};
    double panel_unit_cost{0.0};
    double total_batch_cost{0.0};
    double unit_board_cost{0.0};
};

class CostEstimator {
public:
    [[nodiscard]] static std::expected<PcbCostBreakdown, CalculatorError>
    calculate(const PcbSpecification& spec) noexcept {
        if (spec.dimensions.width_mm <= 0.0 || spec.dimensions.height_mm <= 0.0) {
            return std::unexpected(CalculatorError::InvalidDimensions);
        }
        if (spec.order_quantity <= 0) {
            return std::unexpected(CalculatorError::InvalidQuantity);
        }

        const int n_per_panel = compute_nesting(spec.dimensions);
        if (n_per_panel == 0) {
            return std::unexpected(CalculatorError::ZeroFitOnPanel);
        }

        constexpr double panel_area_sqm = (PanelWidthMm * PanelHeightMm) / 1'000'000.0;
        const double board_area_sqm = spec.dimensions.area_sqm();
        const double board_area_cm2 = spec.dimensions.area_cm2();

        const double util_pct = (static_cast<double>(n_per_panel) * board_area_sqm / panel_area_sqm) * 100.0;

        const double min_feature = std::min(spec.min_trace_mil, spec.min_space_mil);
        const double yield_val = estimate_yield(board_area_cm2, spec.layer_count, min_feature);

        // Множник шаруватості
        const double layer_mult = (spec.layer_count > 2)
            ? 1.0 + 0.42 * static_cast<double>(spec.layer_count - 2)
            : 1.0;

        // Термостійкість Tg
        double tg_mult = 1.0;
        if (spec.tg == TgRating::Mid150) tg_mult = 1.20;
        else if (spec.tg == TgRating::High170) tg_mult = 1.45;

        // Мідне покриття
        const double cu_mult = 1.0 + 0.38 * std::max(0.0, spec.copper_oz - 1.0);

        // Хімічне фінішне покриття
        double finish_adder = 0.0;
        switch (spec.finish) {
            case SurfaceFinish::Enig:         finish_adder = 14.5 * panel_area_sqm; break;
            case SurfaceFinish::Enepig:       finish_adder = 32.0 * panel_area_sqm; break;
            case SurfaceFinish::Osp:          finish_adder = -2.0 * panel_area_sqm; break;
            case SurfaceFinish::HaslLeadFree: finish_adder = 0.0; break;
        }

        // Складність отворів
        double via_mult = spec.has_blind_buried_vias ? 1.65 : 1.0;
        double vippo_cost = (spec.has_vippo && spec.vippo_holes_count > 0)
            ? static_cast<double>(spec.vippo_holes_count) * 0.035
            : 0.0;

        double panel_cost = (panel_area_sqm * BaseFr4CostSqm * tg_mult * layer_mult * cu_mult * via_mult)
                          + finish_adder + vippo_cost;

        // Терміновість
        double rush_mult = 1.0;
        if (spec.turnaround_hours < 120) {
            const double delta = (120.0 - static_cast<double>(spec.turnaround_hours)) / 120.0;
            rush_mult = 1.0 + std::pow(delta, 1.6) * 2.8;
        }
        panel_cost *= rush_mult;

        // NRE витрати
        double nre = BaseNreSetup;
        if (spec.layer_count > 2) nre += static_cast<double>(spec.layer_count - 2) * 28.0;
        if (spec.has_blind_buried_vias) nre += 85.0;
        if (min_feature < 4.0) nre += 50.0;
        nre *= std::min(1.5, rush_mult);

        const int eff_boards_per_panel = std::max(1, static_cast<int>(std::floor(n_per_panel * yield_val)));
        const int panels_needed = (spec.order_quantity + eff_boards_per_panel - 1) / eff_boards_per_panel;

        const double total_variable = static_cast<double>(panels_needed) * panel_cost;
        const double total_batch = nre + total_variable;

        return PcbCostBreakdown{
            .boards_per_panel = n_per_panel,
            .panels_needed = panels_needed,
            .panel_utilization_pct = util_pct,
            .estimated_yield = yield_val,
            .nre_tooling_cost = nre,
            .panel_unit_cost = panel_cost,
            .total_batch_cost = total_batch,
            .unit_board_cost = total_batch / static_cast<double>(spec.order_quantity)
        };
    }

private:
    [[nodiscard]] static int compute_nesting(const BoardDimensions& board) noexcept {
        const double eff_w = PanelWidthMm - 2.0 * PanelMarginMm;
        const double eff_h = PanelHeightMm - 2.0 * PanelMarginMm;

        if (eff_w <= 0.0 || eff_h <= 0.0) return 0;

        const int cols_0  = static_cast<int>(std::floor((eff_w + RouterGapMm) / (board.width_mm + RouterGapMm)));
        const int rows_0  = static_cast<int>(std::floor((eff_h + RouterGapMm) / (board.height_mm + RouterGapMm)));
        const int count_0 = (cols_0 > 0 && rows_0 > 0) ? (cols_0 * rows_0) : 0;

        const int cols_90  = static_cast<int>(std::floor((eff_w + RouterGapMm) / (board.height_mm + RouterGapMm)));
        const int rows_90  = static_cast<int>(std::floor((eff_h + RouterGapMm) / (board.width_mm + RouterGapMm)));
        const int count_90 = (cols_90 > 0 && rows_90 > 0) ? (cols_90 * rows_90) : 0;

        return std::max(count_0, count_90);
    }

    [[nodiscard]] static double estimate_yield(double area_cm2, int layers, double min_feature_mil) noexcept {
        const double feature = std::max(3.0, min_feature_mil);
        const double defect_density = 0.018 * std::pow(6.0 / feature, 1.75) * std::sqrt(static_cast<double>(layers) / 2.0);
        const double y = std::exp(-defect_density * (area_cm2 / 100.0));
        return std::clamp(y, 0.40, 0.99);
    }
};

} // namespace pcb_cost

int main() {
    using namespace pcb_cost;

    const PcbSpecification spec{
        .dimensions = {.width_mm = 85.0, .height_mm = 54.0},
        .layer_count = 4,
        .copper_oz = 1.0,
        .min_trace_mil = 5.0,
        .min_space_mil = 5.0,
        .tg = TgRating::Mid150,
        .finish = SurfaceFinish::Enig,
        .has_blind_buried_vias = false,
        .has_vippo = false,
        .vippo_holes_count = 0,
        .order_quantity = 500,
        .turnaround_hours = 120
    };

    const auto result = CostEstimator::calculate(spec);
    if (!result) {
        std::cerr << "Помилка розрахунку параметрів плати.\n";
        return 1;
    }

    const auto& res = *result;
    std::cout << "=== Результати розрахунку собівартості PCB (C++20) ===\n";
    std::cout << "Розмір плати: " << spec.dimensions.width_mm << " x " << spec.dimensions.height_mm << " мм\n";
    std::cout << "Шари: " << spec.layer_count << ", Покриття: ENIG, Партія: " << spec.order_quantity << " шт.\n";
    std::cout << "Плат на заготовці: " << res.boards_per_panel << " шт. (Утилізація: " << res.panel_utilization_pct << "%)\n";
    std::cout << "Вихід придатних (Yield): " << (res.estimated_yield * 100.0) << "%\n";
    std::cout << "Необхідно панелей: " << res.panels_needed << " шт.\n";
    std::cout << "NRE підготовка виробництва: $" << res.nre_tooling_cost << "\n";
    std::cout << "Собівартість 1 панелі: $" << res.panel_unit_cost << "\n";
    std::cout << "Повна собівартість партії: $" << res.total_batch_cost << "\n";
    std::cout << "Ціна 1 готової плати: $" << res.unit_board_cost << "\n";

    return 0;
}
