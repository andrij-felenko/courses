#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <expected>
#include <string_view>
#include <span>

enum class LeadType {
    GullWing,
    FlatNoLead,
    RectangularChip,
    JLead,
    BallGridArray
};

enum class DensityLevel {
    LevelA_Most,
    LevelB_Nominal,
    LevelC_Least
};

struct ComponentDimensions {
    double l_min{0.0}, l_max{0.0}; // Повний габарит
    double s_min{0.0}, s_max{0.0}; // Внутрішній просвіт
    double w_min{0.0}, w_max{0.0}; // Ширина виводу
    double t_min{0.0}, t_max{0.0}; // Довжина стопи
    double pitch{0.0};             // Крок виводів
};

struct ProcessTolerances {
    double fabrication_f{0.10};
    double placement_p{0.05};
    double mask_expansion{0.05};
    double min_mask_dam{0.075};
};

struct FilletGoals {
    double jt{0.0};
    double jh{0.0};
    double js{0.0};
    double excess{0.0};
};

struct LandPattern {
    double z_max{0.0};
    double g_min{0.0};
    double x_max{0.0};
    double pad_length_y{0.0};
    double center_dist_c{0.0};
    double courtyard_x{0.0};
    double courtyard_y{0.0};
    double actual_mask_dam{0.0};
    bool is_mask_dam_ok{false};
    bool is_nsmd_recommended{false};
};

struct StencilWindowMatrix {
    int cols{1};
    int rows{1};
    double window_width{0.0};
    double window_length{0.0};
    double coverage_ratio{0.0};
};

enum class CalculationError {
    InvalidComponentDimensions,
    NegativeHeelClearance,
    InvalidProcessTolerances
};

class IPC7351Calculator {
public:
    [[nodiscard]] static constexpr FilletGoals get_goals(LeadType type, DensityLevel level) noexcept {
        switch (type) {
            case LeadType::GullWing:
                if (level == DensityLevel::LevelA_Most) return {0.55, 0.45, 0.05, 0.50};
                if (level == DensityLevel::LevelB_Nominal) return {0.35, 0.35, 0.03, 0.25};
                return {0.15, 0.25, 0.01, 0.10};
            case LeadType::FlatNoLead:
                if (level == DensityLevel::LevelA_Most) return {0.30, 0.00, 0.05, 0.50};
                if (level == DensityLevel::LevelB_Nominal) return {0.20, 0.00, 0.00, 0.25};
                return {0.10, 0.00, -0.04, 0.10};
            case LeadType::RectangularChip:
                if (level == DensityLevel::LevelA_Most) return {0.40, 0.00, 0.10, 0.50};
                if (level == DensityLevel::LevelB_Nominal) return {0.30, 0.00, 0.05, 0.25};
                return {0.15, 0.00, 0.00, 0.10};
            case LeadType::JLead:
                if (level == DensityLevel::LevelA_Most) return {0.70, 0.35, 0.10, 0.50};
                if (level == DensityLevel::LevelB_Nominal) return {0.50, 0.25, 0.05, 0.25};
                return {0.30, 0.15, 0.00, 0.10};
            default:
                return {0.25, 0.25, 0.03, 0.25};
        }
    }

    [[nodiscard]] static std::expected<LandPattern, CalculationError> 
    calculate(const ComponentDimensions& comp, LeadType type, DensityLevel level, const ProcessTolerances& proc) noexcept {
        if (comp.l_max <= comp.l_min || comp.w_max <= comp.w_min) {
            return std::unexpected(CalculationError::InvalidComponentDimensions);
        }

        const auto goals = get_goals(type, level);

        const double c_l = comp.l_max - comp.l_min;
        const double c_s = comp.s_max - comp.s_min;
        const double c_w = comp.w_max - comp.w_min;

        const double f2_p2 = (proc.fabrication_f * proc.fabrication_f) + (proc.placement_p * proc.placement_p);
        const double t_l = std::sqrt((c_l * c_l) + f2_p2);
        const double t_s = std::sqrt((c_s * c_s) + f2_p2);
        const double t_w = std::sqrt((c_w * c_w) + f2_p2);

        const double z_max = comp.l_min + (2.0 * goals.jt) + t_l;
        const double g_min = comp.s_max - (2.0 * goals.jh) - t_s;
        const double x_max = comp.w_min + (2.0 * goals.js) + t_w;

        if (g_min < 0.0) {
            return std::unexpected(CalculationError::NegativeHeelClearance);
        }

        const double pad_y = (z_max - g_min) / 2.0;
        const double center_c = (z_max + g_min) / 2.0;

        double actual_dam = 0.0;
        bool dam_ok = true;
        bool nsmd_req = false;

        if (comp.pitch > 0.0) {
            const double copper_gap = comp.pitch - x_max;
            actual_dam = copper_gap - (2.0 * proc.mask_expansion);
            dam_ok = (actual_dam >= proc.min_mask_dam);
            nsmd_req = (comp.pitch <= 0.50);
        }

        return LandPattern{
            .z_max = z_max,
            .g_min = g_min,
            .x_max = x_max,
            .pad_length_y = pad_y,
            .center_dist_c = center_c,
            .courtyard_x = z_max + (2.0 * goals.excess),
            .courtyard_y = comp.w_max + (2.0 * goals.excess),
            .actual_mask_dam = actual_dam,
            .is_mask_dam_ok = dam_ok,
            .is_nsmd_recommended = nsmd_req
        };
    }

    [[nodiscard]] static StencilWindowMatrix 
    calculate_stencil_matrix(double pad_w, double pad_h, int cols, int rows, double bridge_w) noexcept {
        const double win_w = (pad_w - ((cols - 1) * bridge_w)) / cols;
        const double win_h = (pad_h - ((rows - 1) * bridge_w)) / rows;
        const double paste_area = (win_w * win_h) * (cols * rows);
        const double total_area = pad_w * pad_h;

        return StencilWindowMatrix{
            .cols = cols,
            .rows = rows,
            .window_width = win_w,
            .window_length = win_h,
            .coverage_ratio = paste_area / total_area
        };
    }
};

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++20 IPC-7351 LAND PATTERN SUITE ===\n\n";

    constexpr ProcessTolerances proc{
        .fabrication_f = 0.10,
        .placement_p = 0.05,
        .mask_expansion = 0.04,
        .min_mask_dam = 0.075
    };

    // Верифікаційний тест TSSOP-20 (Pitch = 0.65 mm)
    constexpr ComponentDimensions tssop20{
        .l_min = 6.20, .l_max = 6.60,
        .s_min = 4.30, .s_max = 4.50,
        .w_min = 0.19, .w_max = 0.30,
        .t_min = 0.45, .t_max = 0.75,
        .pitch = 0.65
    };

    const auto result = IPC7351Calculator::calculate(tssop20, LeadType::GullWing, DensityLevel::LevelB_Nominal, proc);

    if (result.has_value()) {
        std::cout << "[TSSOP-20 Gull-Wing (Pitch 0.65 mm)]\n";
        std::cout << "  Розмір площадки Y x X: " << result->pad_length_y << " x " << result->x_max << " mm\n";
        std::cout << "  Міжцентрова відстань C: " << result->center_dist_c << " mm\n";
        std::cout << "  Місток маски: " << result->actual_mask_dam << " mm (" 
                  << (result->is_mask_dam_ok ? "ПРОЙДЕНО" : "ЗАМИКАННЯ") << ")\n";
        std::cout << "  Дворик Courtyard X x Y: " << result->courtyard_x << " x " << result->courtyard_y << " mm\n";
    }

    return 0;
}
