#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

struct PcbGeometry {
    double trace_w_mm{0.35};       // Ширина доріжки
    double trace_t_mm{0.035};      // Товщина фольги (1 oz)
    double trace_len_mm{30.0};     // Довжина доріжки
    double diel_h_mm{0.20};        // Висота діелектрика
    double diel_er{4.2};           // Діелектрична проникність FR-4
    double sig_i_ma{40.0};         // Струм сигналу
    double sig_tr_ns{0.8};         // Час наростання фронту
    double slot_detour_mm{14.0};   // Довжина обходу розрізу
    double via_h_mm{1.2};          // Висота сигнального via
    double via_d_mm{0.30};         // Діаметр via
    double via_ret_dist_mm{0.70};  // Відстань до return via
    double iso_ret_dist_mm{12.0};  // Відстань до випадкового via без пари
};

struct ReturnPathMetrics {
    double f_crossover_khz;
    double l_solid_nh;
    double l_detour_nh;
    double v_bounce_solid_mv;
    double v_bounce_detour_mv;
    double l_via_iso_nh;
    double l_via_1ret_nh;
    double l_via_2ret_nh;
    double l_via_4ret_nh;
    double emi_increase_db;
};

class ReturnPathAnalyzer {
public:
    static constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;
    static constexpr double rho_copper = 1.72e-8; // Ом*м

    [[nodiscard]] static ReturnPathMetrics analyze(const PcbGeometry& g) noexcept {
        ReturnPathMetrics m{};

        // Опір постійному струму
        const double area_m2 = (g.trace_w_mm * 1e-3) * (g.trace_t_mm * 1e-3);
        const double r_dc = rho_copper * (g.trace_len_mm * 1e-3) / area_m2;

        // Індуктивність мікросмужки над суцільною площиною
        const double w_eff = 0.8 * g.trace_w_mm + g.trace_t_mm;
        const double l_per_meter = (mu_0 / (2.0 * std::numbers::pi)) * 
                                   std::log(5.98 * g.diel_h_mm / w_eff);
        const double l_solid_h = std::max(l_per_meter, 1e-7) * (g.trace_len_mm * 1e-3);
        m.l_solid_nh = l_solid_h * 1e9;

        // Частота кросоверу f_c = R / (2*pi*L)
        m.f_crossover_khz = (r_dc / (2.0 * std::numbers::pi * l_solid_h)) / 1e3;

        // Індуктивність обходу розрізу
        const double s_m = g.slot_detour_mm * 1e-3;
        const double r_eff = 0.2235 * ((g.trace_w_mm + g.trace_t_mm) * 1e-3);
        const double delta_l_h = std::max(0.0, 
            (mu_0 * s_m / (2.0 * std::numbers::pi)) * (std::log(2.0 * s_m / r_eff) - 0.75));
        m.l_detour_nh = m.l_solid_nh + (delta_l_h * 1e9);

        // Падіння напруги / викид V = L * di/dt
        const double didt = (g.sig_i_ma * 1e-3) / (g.sig_tr_ns * 1e-9);
        m.v_bounce_solid_mv = (l_solid_h * didt) * 1e3;
        m.v_bounce_detour_mv = ((l_solid_h + delta_l_h) * didt) * 1e3;

        // Індуктивність сигнального перехідного отвору
        const double via_h_m = g.via_h_mm * 1e-3;
        const double via_r_m = (g.via_d_mm * 0.5) * 1e-3;
        const double d_iso_m = g.iso_ret_dist_mm * 1e-3;
        const double s_ret_m = g.via_ret_dist_mm * 1e-3;

        m.l_via_iso_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                          (std::log(2.0 * d_iso_m / via_r_m) + 0.25)) * 1e9;

        m.l_via_1ret_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                           (std::log(s_ret_m / via_r_m) + 0.25)) * 1e9;

        m.l_via_2ret_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                           (std::log(s_ret_m / via_r_m) / 2.0 + 0.125)) * 1e9;

        m.l_via_4ret_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                           (std::log(s_ret_m / via_r_m) / 4.0 + 0.0625)) * 1e9;

        // Зростання випромінювання петлі EMI (дБ)
        const double a_solid = g.trace_len_mm * g.diel_h_mm;
        const double a_split = a_solid + (g.slot_detour_mm * g.slot_detour_mm * 0.25);
        m.emi_increase_db = 20.0 * std::log10(a_split / a_solid);

        return m;
    }
};

int main() {
    constexpr PcbGeometry geom{};
    const auto res = ReturnPathAnalyzer::analyze(geom);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "===============================================================\n";
    std::cout << "   АНАЛІЗАТОР ПЕТЛІ ЗВОРОТНОГО СТРУМУ ДРУКОВАНОЇ ПЛАТИ (C++20) \n";
    std::cout << "===============================================================\n";
    std::cout << "1. РЕЖИМИ ТЕЧІЇ СТРУМУ:\n";
    std::cout << "  Частота кросоверу f_c (R vs L):  " << res.f_crossover_khz << " кГц\n\n";

    std::cout << "2. ПАРАЗИТНА ІНДУКТИВНІСТЬ ТА ДЗВІН ПРИ РОЗРІЗІ ПЛОЩИНИ:\n";
    std::cout << "  Індуктивність над суцільною площиною:  " << std::setw(6) << res.l_solid_nh 
              << " нГн  (V_drop = " << std::setw(5) << res.v_bounce_solid_mv << " мВ)\n";
    std::cout << "  Індуктивність при обході розрізу:      " << std::setw(6) << res.l_detour_nh 
              << " нГн  (V_drop = " << std::setw(5) << res.v_bounce_detour_mv << " мВ)\n";
    std::cout << "  Зростання випромінювання петлі (EMI):  +" << res.emi_increase_db << " дБ\n\n";

    std::cout << "3. ІНДУКТИВНІСТЬ ПЕРЕХОДУ МІЖ ШАРАМИ (VIA TRANSITION):\n";
    std::cout << "  Без return via (d_iso = " << geom.iso_ret_dist_mm << " мм):      " 
              << std::setw(6) << res.l_via_iso_nh << " нГн\n";
    std::cout << "  З 1 return via (відстань " << geom.via_ret_dist_mm << " мм):     " 
              << std::setw(6) << res.l_via_1ret_nh << " нГн  (x" 
              << (res.l_via_iso_nh / res.l_via_1ret_nh) << " менше)\n";
    std::cout << "  З 2 return vias (симетричні):          " 
              << std::setw(6) << res.l_via_2ret_nh << " нГн  (x" 
              << (res.l_via_iso_nh / res.l_via_2ret_nh) << " менше)\n";
    std::cout << "  З 4 return vias (квадро-кільце):       " 
              << std::setw(6) << res.l_via_4ret_nh << " нГн  (x" 
              << (res.l_via_iso_nh / res.l_via_4ret_nh) << " менше)\n";
    std::cout << "===============================================================\n";

    return 0;
}
