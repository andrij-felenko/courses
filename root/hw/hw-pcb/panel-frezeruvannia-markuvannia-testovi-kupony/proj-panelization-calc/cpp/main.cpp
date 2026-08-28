#include <iostream>
#include <iomanip>
#include <string_view>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <optional>
#include <numbers>

namespace pcb::panel {

constexpr double DefaultFr4FlexuralStrengthMpa = 380.0;
constexpr double DefaultFr4YoungModulusMpa      = 22000.0;
constexpr double DefaultFr4ShearStrengthMpa     = 75.0;

enum class ComponentClass : uint8_t {
    Mlcc0402,
    Mlcc0603,
    Mlcc0805,
    Mlcc1206,
    BgaFinePitch
};

struct BoardGeometry {
    double length_mm{65.0};
    double width_mm{42.0};
    double thickness_mm{1.60};

    [[nodiscard]] constexpr double area() const noexcept {
        return length_mm * width_mm;
    }
};

struct PanelLimits {
    double max_length_mm{300.0};
    double max_width_mm{200.0};
    double rail_width_mm{7.0};
    double route_slot_width_mm{2.0};
};

struct TabSpecification {
    double tab_width_mm{4.0};
    double hole_diameter_mm{0.60};
    double hole_pitch_mm{1.00};
    int hole_count{4};
    double inset_offset_mm{0.15};
    double lever_arm_mm{15.0};
};

struct LayoutEvaluation {
    int count_x{0};
    int count_y{0};
    int total_boards{0};
    double actual_length_mm{0.0};
    double actual_width_mm{0.0};
    double utilization_percentage{0.0};
    bool is_rotated_90deg{false};
};

struct TabAnalysisResult {
    double net_solid_width_mm{0.0};
    double net_shear_area_mm2{0.0};
    double section_modulus_mm3{0.0};
    double breaking_moment_n_mm{0.0};
    double breaking_force_n{0.0};
    double shear_capacity_n{0.0};
    double stress_concentration_kt{0.0};
    double keepout_mlcc0402_mm{0.0};
    double keepout_mlcc0805_mm{0.0};
    double keepout_mlcc1206_mm{0.0};
};

class PanelizationOptimizer {
public:
    [[nodiscard]] static constexpr double GetStrainLimit(ComponentClass comp) noexcept {
        switch (comp) {
            case ComponentClass::Mlcc0402:      return 1000.0e-6;
            case ComponentClass::Mlcc0603:      return 750.0e-6;
            case ComponentClass::Mlcc0805:      return 500.0e-6;
            case ComponentClass::Mlcc1206:      return 350.0e-6;
            case ComponentClass::BgaFinePitch: return 300.0e-6;
        }
        return 500.0e-6;
    }

    [[nodiscard]] static double CalculatePetersonKt(double d_hole, double pitch) noexcept {
        if (pitch <= 0.0 || d_hole <= 0.0) return 3.0;
        double r = std::min(d_hole / pitch, 0.90);
        return 3.0 - 3.13 * r + 3.66 * (r * r) - 1.53 * (r * r * r);
    }

    [[nodiscard]] static std::expected<LayoutEvaluation, std::string_view> OptimizeLayout(
        const BoardGeometry& board,
        const PanelLimits& panel) noexcept
    {
        if (board.length_mm <= 0.0 || board.width_mm <= 0.0 || board.thickness_mm <= 0.0) {
            return std::unexpected("Некоректні габарити друкованої плати");
        }
        if (panel.max_length_mm <= 2.0 * panel.rail_width_mm || panel.max_width_mm <= 2.0 * panel.rail_width_mm) {
            return std::unexpected("Габарити панелі менші за технологічні рейки");
        }

        double avail_x = panel.max_length_mm - 2.0 * panel.rail_width_mm + panel.route_slot_width_mm;
        double avail_y = panel.max_width_mm  - 2.0 * panel.rail_width_mm + panel.route_slot_width_mm;

        // Пряма конфігурація (0°)
        int nx1 = static_cast<int>(std::floor(avail_x / (board.length_mm + panel.route_slot_width_mm)));
        int ny1 = static_cast<int>(std::floor(avail_y / (board.width_mm  + panel.route_slot_width_mm)));
        int tot1 = (nx1 > 0 && ny1 > 0) ? (nx1 * ny1) : 0;
        double len1 = (nx1 > 0) ? (nx1 * board.length_mm + (nx1 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double wid1 = (ny1 > 0) ? (ny1 * board.width_mm  + (ny1 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double util1 = (len1 > 0.0 && wid1 > 0.0) ? ((tot1 * board.area()) / (len1 * wid1) * 100.0) : 0.0;

        // Розвернута конфігурація (90°)
        int nx2 = static_cast<int>(std::floor(avail_x / (board.width_mm  + panel.route_slot_width_mm)));
        int ny2 = static_cast<int>(std::floor(avail_y / (board.length_mm + panel.route_slot_width_mm)));
        int tot2 = (nx2 > 0 && ny2 > 0) ? (nx2 * ny2) : 0;
        double len2 = (nx2 > 0) ? (nx2 * board.width_mm  + (nx2 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double wid2 = (ny2 > 0) ? (ny2 * board.length_mm + (ny2 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double util2 = (len2 > 0.0 && wid2 > 0.0) ? ((tot2 * board.area()) / (len2 * wid2) * 100.0) : 0.0;

        LayoutEvaluation result;
        if (tot2 > tot1 || (tot2 == tot1 && util2 > util1)) {
            result.count_x = nx2;
            result.count_y = ny2;
            result.total_boards = tot2;
            result.actual_length_mm = len2;
            result.actual_width_mm = wid2;
            result.utilization_percentage = util2;
            result.is_rotated_90deg = true;
        } else {
            result.count_x = nx1;
            result.count_y = ny1;
            result.total_boards = tot1;
            result.actual_length_mm = len1;
            result.actual_width_mm = wid1;
            result.utilization_percentage = util1;
            result.is_rotated_90deg = false;
        }

        if (result.total_boards == 0) {
            return std::unexpected("Плата не вміщується на панель із заданими рейками та пазами");
        }

        return result;
    }

    [[nodiscard]] static TabAnalysisResult AnalyzeTab(
        const TabSpecification& tab,
        double pcb_thickness_mm) noexcept
    {
        TabAnalysisResult res;
        double holes_total_width = tab.hole_count * tab.hole_diameter_mm;
        res.net_solid_width_mm = std::max(0.20, tab.tab_width_mm - holes_total_width);
        res.net_shear_area_mm2 = res.net_solid_width_mm * pcb_thickness_mm;
        res.section_modulus_mm3 = (res.net_solid_width_mm * pcb_thickness_mm * pcb_thickness_mm) / 6.0;

        res.breaking_moment_n_mm = DefaultFr4FlexuralStrengthMpa * res.section_modulus_mm3;
        double lever = std::max(1.0, tab.lever_arm_mm);
        res.breaking_force_n = res.breaking_moment_n_mm / lever;
        res.shear_capacity_n = DefaultFr4ShearStrengthMpa * res.net_shear_area_mm2;

        res.stress_concentration_kt = CalculatePetersonKt(tab.hole_diameter_mm, tab.hole_pitch_mm);

        res.keepout_mlcc0402_mm = ComputeKeepoutDistance(res.breaking_force_n, lever, tab.tab_width_mm, pcb_thickness_mm, GetStrainLimit(ComponentClass::Mlcc0402));
        res.keepout_mlcc0805_mm = ComputeKeepoutDistance(res.breaking_force_n, lever, tab.tab_width_mm, pcb_thickness_mm, GetStrainLimit(ComponentClass::Mlcc0805));
        res.keepout_mlcc1206_mm = ComputeKeepoutDistance(res.breaking_force_n, lever, tab.tab_width_mm, pcb_thickness_mm, GetStrainLimit(ComponentClass::Mlcc1206));

        return res;
    }

private:
    [[nodiscard]] static double ComputeKeepoutDistance(
        double force_n, double lever_arm_mm, double tab_w_mm, double thickness_mm, double limit_strain) noexcept
    {
        if (limit_strain <= 0.0 || thickness_mm <= 0.0 || tab_w_mm <= 0.0) return 0.50;
        double num = 6.0 * force_n * lever_arm_mm;
        double den = tab_w_mm * thickness_mm * thickness_mm * DefaultFr4YoungModulusMpa * limit_strain;
        if (num <= den) return 0.50;
        double d = 2.0 * thickness_mm * std::log(num / den);
        return std::max(0.50, d);
    }
};

void PrintReport(const BoardGeometry& board, const PanelLimits& panel,
                 const TabSpecification& tab, const LayoutEvaluation& layout,
                 const TabAnalysisResult& mech)
{
    std::cout << "================================================================================\n"
              << "  C++20 ІНЖЕНЕРНИЙ ЗВІТ РОЗРАХУНКУ ПАНЕЛІ ТА ПЕРЕМИЧОК SMT\n"
              << "================================================================================\n\n"
              << "1. ПАРАМЕТРИ ПЛАТИ ТА ПАНЕЛІ:\n"
              << "   Плата (L x W x T):               " << board.length_mm << " x " << board.width_mm << " x " << board.thickness_mm << " мм\n"
              << "   Ліміт панелі (L_max x W_max):    " << panel.max_length_mm << " x " << panel.max_width_mm << " мм\n"
              << "   Технологічні поля (Rails):       " << panel.rail_width_mm << " мм | Паз фрези: " << panel.route_slot_width_mm << " мм\n\n"
              << "2. ОПТИМАЛЬНА РОЗКЛАДКА (2D ARRAY PACKING):\n"
              << "   Орієнтація:                      " << (layout.is_rotated_90deg ? "Поворот 90°" : "Пряма (0°)") << "\n"
              << "   Матриця компонування (Nx x Ny):  " << layout.count_x << " x " << layout.count_y << " шт.\n"
              << "   Вихід плат з однієї панелі:      " << layout.total_boards << " шт.\n"
              << "   Розміри сформованої панелі:      " << layout.actual_length_mm << " x " << layout.actual_width_mm << " мм\n"
              << "   Коефіцієнт використання матеріалу: " << std::fixed << std::setprecision(2) << layout.utilization_percentage << " %\n\n"
              << "3. МІЦНІСНИЙ АНАЛІЗ ПЕРЕМИЧОК (MOUSE BITES BREAKAWAY TAB):\n"
              << "   Ширина перемички (W_tab):        " << tab.tab_width_mm << " мм\n"
              << "   Перфорація:                      " << tab.hole_count << " отворів Ø" << tab.hole_diameter_mm
              << " мм з кроком " << tab.hole_pitch_mm << " мм\n"
              << "   Залишкова ширина суцільної міді: " << mech.net_solid_width_mm << " мм\n"
              << "   Коефіцієнт концентрації (Kt):    " << mech.stress_concentration_kt << "\n"
              << "   Згинальний момент руйнування:    " << mech.breaking_moment_n_mm << " Н·мм\n"
              << "   Зусилля виламування (Force):     " << mech.breaking_force_n << " Н ("
              << (mech.breaking_force_n / 9.80665) << " кгс) при плечі " << tab.lever_arm_mm << " мм\n"
              << "   Зусилля зсуву (Shear):           " << mech.shear_capacity_n << " Н\n\n"
              << "4. ЗОНИ ЗАБОРОНИ КОМПОНЕНТІВ ЗА IPC-9704:\n"
              << "   Keepout для MLCC 0402 (1000 µε):  d >= " << mech.keepout_mlcc0402_mm << " мм\n"
              << "   Keepout для MLCC 0805 (500 µε):   d >= " << mech.keepout_mlcc0805_mm << " мм\n"
              << "   Keepout для MLCC 1206 (350 µε):   d >= " << mech.keepout_mlcc1206_mm << " мм\n"
              << "   Рекомендований відступ отворів:  " << tab.inset_offset_mm << " мм (Inset всередину контуру)\n"
              << "================================================================================\n";
}

} // namespace pcb::panel

int main(int argc, char** argv) {
    using namespace pcb::panel;

    BoardGeometry board{.length_mm = 65.0, .width_mm = 42.0, .thickness_mm = 1.60};
    PanelLimits panel{.max_length_mm = 300.0, .max_width_mm = 200.0, .rail_width_mm = 7.0, .route_slot_width_mm = 2.0};
    TabSpecification tab{.tab_width_mm = 4.0, .hole_diameter_mm = 0.60, .hole_pitch_mm = 1.00, .hole_count = 4, .inset_offset_mm = 0.15, .lever_arm_mm = 15.0};

    if (argc >= 3) {
        board.length_mm = std::stod(argv[1]);
        board.width_mm = std::stod(argv[2]);
    }
    if (argc >= 4) {
        board.thickness_mm = std::stod(argv[3]);
    }

    auto layout_res = PanelizationOptimizer::OptimizeLayout(board, panel);
    if (!layout_res) {
        std::cerr << "Помилка панелізації: " << layout_res.error() << "\n";
        return 1;
    }

    TabAnalysisResult mech_res = PanelizationOptimizer::AnalyzeTab(tab, board.thickness_mm);

    PrintReport(board, panel, tab, *layout_res, mech_res);

    return 0;
}
