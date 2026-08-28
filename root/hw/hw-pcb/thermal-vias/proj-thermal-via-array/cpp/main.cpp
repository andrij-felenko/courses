#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

struct ThermalParams {
    double pcb_thickness_m{1.6e-3};      // Товщина плати (h), м
    double via_drill_diam_m{3.0e-4};     // Діаметр свердла via (d), м
    double via_plating_thk_m{2.5e-5};    // Товщина міднення стінки (t), м
    int    via_count{16};                // Кількість отворів (N)
    double pad_side_a_m{5.0e-3};         // Сторона прямокутного термопада (a), м
    double pad_side_b_m{5.0e-3};         // Сторона прямокутного термопада (b), м
    double plane_radius_m{2.5e-2};       // Ефективний радіус розтікання міді, м
    double plane_copper_thk_m{3.5e-5};   // Товщина мідного полігону, м
    double r_jc_k_w{2.0};                // Опір кристал-корпус (R_theta_JC), К/Вт
    double r_tim_k_w{3.0};               // Опір термоінтерфейсу (R_theta_TIM), К/Вт
    double r_hs_k_w{6.0};                // Опір радіатора (R_theta_HS), К/Вт
    double ambient_temp_c{25.0};         // Температура середовища (T_A), °C
    double power_dissipation_w{4.6};     // Потужність розсіювання (P), Вт
};

struct ThermalReport {
    double single_via_area_m2{0.0};
    double single_via_rth_k_w{0.0};
    double array_rth_k_w{0.0};
    double solder_rth_k_w{0.0};
    double plane_spread_rth_k_w{0.0};
    double total_rth_ja_k_w{0.0};
    double junction_temp_c{0.0};
    bool   solder_wicking_risk{false};
    bool   is_safe_temp{true};
};

class ThermalSolver {
public:
    static constexpr double kCopper = 385.0; // Вт/(м·К)
    static constexpr double kSolder = 58.0;  // Вт/(м·К)

    [[nodiscard]] static ThermalReport solve(const ThermalParams& p) noexcept {
        ThermalReport rep;

        // 1. Площа поперечного перерізу та опір одного via
        const double d = p.via_drill_diam_m;
        const double t = p.via_plating_thk_m;
        rep.single_via_area_m2 = std::numbers::pi * (d * t - t * t);
        rep.single_via_rth_k_w = p.pcb_thickness_m / (kCopper * rep.single_via_area_m2);

        // 2. Паралельний опір масиву
        rep.array_rth_k_w = rep.single_via_rth_k_w / static_cast<double>(p.via_count);

        // 3. Опір шару припою (товщина 50 мкм)
        const double pad_area = p.pad_side_a_m * p.pad_side_b_m;
        constexpr double solder_thk = 5.0e-5; // 50 мкм
        rep.solder_rth_k_w = solder_thk / (kSolder * pad_area);

        // 4. Опір розтікання у нижньому мідному полігоні
        const double r_pad_eff = std::sqrt(pad_area / std::numbers::pi);
        if (p.plane_radius_m > r_pad_eff && p.plane_copper_thk_m > 0.0) {
            rep.plane_spread_rth_k_w = std::log(p.plane_radius_m / r_pad_eff) /
                                       (2.0 * std::numbers::pi * kCopper * p.plane_copper_thk_m);
        } else {
            rep.plane_spread_rth_k_w = 0.0;
        }

        // 5. Повний тепловий опір
        rep.total_rth_ja_k_w = p.r_jc_k_w + rep.solder_rth_k_w + rep.array_rth_k_w +
                               rep.plane_spread_rth_k_w + p.r_tim_k_w + p.r_hs_k_w;

        // 6. Температура переходу
        rep.junction_temp_c = p.ambient_temp_c + p.power_dissipation_w * rep.total_rth_ja_k_w;

        // 7. Технологічні верифікації
        rep.solder_wicking_risk = (p.via_drill_diam_m > 3.5e-4);
        rep.is_safe_temp = (rep.junction_temp_c <= 125.0);

        return rep;
    }
};

int main() {
    ThermalParams config{
        .pcb_thickness_m     = 1.6e-3,
        .via_drill_diam_m    = 3.0e-4,
        .via_plating_thk_m   = 2.5e-5,
        .via_count           = 16,
        .pad_side_a_m        = 5.0e-3,
        .pad_side_b_m        = 5.0e-3,
        .plane_radius_m      = 2.5e-2,
        .plane_copper_thk_m  = 3.5e-5,
        .r_jc_k_w            = 2.0,
        .r_tim_k_w           = 3.0,
        .r_hs_k_w            = 6.0,
        .ambient_temp_c      = 25.0,
        .power_dissipation_w = 4.6
    };

    const auto report = ThermalSolver::solve(config);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ЗВІТ ТЕПЛОВОГО РОЗРАХУНКУ ===\n";
    std::cout << "Одиничний via: площа Cu = " << report.single_via_area_m2 * 1.0e6 
              << " мм², R_th = " << report.single_via_rth_k_w << " К/Вт\n";
    std::cout << "Масив із " << config.via_count << " via: R_th = " << report.array_rth_k_w << " К/Вт\n";
    std::cout << "Шар припою: R_th = " << std::setprecision(3) << report.solder_rth_k_w << " К/Вт\n";
    std::cout << std::setprecision(2);
    std::cout << "Розтікання у міді: R_th = " << report.plane_spread_rth_k_w << " К/Вт\n";
    std::cout << "Повний опір R_th(JA): " << report.total_rth_ja_k_w << " К/Вт\n";
    std::cout << "Температура кристала T_J: " << report.junction_temp_c << " °C\n";
    std::cout << "Ризик втягування припою: " 
              << (report.solder_wicking_risk ? "ТАК (d > 0.35 мм!)" : "НІ (норма)") << "\n";
    std::cout << "Статус безпеки кристала: " 
              << (report.is_safe_temp ? "НОРМА (T_J <= 125 °C)" : "ПЕРЕГРІВ!") << "\n";

    return 0;
}
