#include <iostream>
#include <cmath>
#include <iomanip>
#include <string_view>

namespace mech {

struct ToleranceChainInput {
    double nom_enclosure_width{0.0};
    double tol_enclosure{0.0};
    double nom_pcb_width{0.0};
    double tol_pcb_milling{0.0};
    double tol_drill_drift{0.0};
    double tol_screw_play{0.0};
};

struct ToleranceReport {
    double min_clearance_worst_case{0.0};
    double min_clearance_rss{0.0};
    double max_clearance_worst_case{0.0};
    double max_clearance_rss{0.0};
    bool is_assemblable{false};
};

class ToleranceAnalyzer {
public:
    [[nodiscard]] static constexpr ToleranceReport evaluate(const ToleranceChainInput& in) noexcept {
        ToleranceReport rep{};
        const double nom_clearance = in.nom_enclosure_width - in.nom_pcb_width;

        // Worst-Case оцінка
        const double sum_tol_worst = in.tol_enclosure + in.tol_pcb_milling + 
                                     in.tol_drill_drift + in.tol_screw_play;
        rep.min_clearance_worst_case = nom_clearance - sum_tol_worst;
        rep.max_clearance_worst_case = nom_clearance + sum_tol_worst;

        // RSS статистична оцінка
        const double sum_sq = (in.tol_enclosure * in.tol_enclosure) +
                              (in.tol_pcb_milling * in.tol_pcb_milling) +
                              (in.tol_drill_drift * in.tol_drill_drift) +
                              (in.tol_screw_play * in.tol_screw_play);
        const double sum_tol_rss = std::sqrt(sum_sq);

        rep.min_clearance_rss = nom_clearance - sum_tol_rss;
        rep.max_clearance_rss = nom_clearance + sum_tol_rss;

        rep.is_assemblable = (rep.min_clearance_rss > 0.15); // Поріг 150 мкм
        return rep;
    }

    [[nodiscard]] static constexpr double calculate_mlcc_safe_radius(
        double screw_head_radius, double pcb_thickness, double safety_factor = 2.5) noexcept 
    {
        return screw_head_radius + (safety_factor * pcb_thickness);
    }
};

} // namespace mech

int main() {
    constexpr mech::ToleranceChainInput input{
        .nom_enclosure_width = 122.0,
        .tol_enclosure       = 0.25,
        .nom_pcb_width       = 120.0,
        .tol_pcb_milling     = 0.15,
        .tol_drill_drift     = 0.08,
        .tol_screw_play      = 0.10
    };

    const auto rep = mech::ToleranceAnalyzer::evaluate(input);

    std::cout << "--- АНАЛІЗ РОЗМІРНИХ ЛАНЦЮГІВ ДРУКОВАНОЇ ПЛАТИ (C++20) ---\n"
              << std::fixed << std::setprecision(3)
              << "Номінальний зазор: " << (input.nom_enclosure_width - input.nom_pcb_width) << " мм\n"
              << "Worst-Case зазор : [" << rep.min_clearance_worst_case << " .. " 
              << rep.max_clearance_worst_case << "] мм\n"
              << "RSS зазор (3-sigma): [" << rep.min_clearance_rss << " .. " 
              << rep.max_clearance_rss << "] мм\n"
              << "Статус збирання  : " << (rep.is_assemblable ? "ПРИДАТНО (PASS)" : "РИЗИК ЗАКЛИНЮВАННЯ (FAIL)") 
              << "\n\n";

    constexpr double r_screw_m3 = 3.0;
    constexpr double t_pcb = 1.6;
    constexpr double r_safe = mech::ToleranceAnalyzer::calculate_mlcc_safe_radius(r_screw_m3, t_pcb, 2.5);

    std::cout << "--- РОЗРАХУНОК ЗОНИ БЕЗПЕКИ MLCC (M3 ГВИНТ) ---\n"
              << "Радіус шайби гвинта : " << r_screw_m3 << " мм\n"
              << "Товщина діелектрика : " << t_pcb << " мм\n"
              << "Безпечний радіус MLCC: " << r_safe << " мм (діаметр заборони " 
              << (r_safe * 2.0) << " мм)\n";

    return 0;
}
