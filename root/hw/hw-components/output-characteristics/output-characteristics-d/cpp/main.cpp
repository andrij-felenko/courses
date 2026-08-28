#include <iostream>
#include <iomanip>
#include <algorithm>
#include <cmath>

struct StageConfig {
    double v_cc{12.0};      // Напруга живлення (В)
    double r_c{1000.0};     // Опір колектора (Ом)
    double r_e{200.0};      // Опір емітера (Ом)
    double r_l{2000.0};     // Опір навантаження (Ом)
    double v_a{100.0};      // Напруга Ерлі (В)
    double v_ce_sat{0.2};   // Напруга насичення (В)
    double i_cq{0.005};     // Струм спокою колектора (А)
};

struct AnalysisResult {
    double v_ceq{0.0};        // Напруга спокою колектор-емітер (В)
    double r_ac{0.0};         // Динамічний опір навантаження (Ом)
    double r_o{0.0};          // Вихідний диференційний опір (Ом)
    double v_pp_max{0.0};     // Максимальний розмах пік-до-піку (В)
    bool is_clipping_sym{false}; // Прапорець симетричності розмаху
};

constexpr AnalysisResult analyze_bjt_stage(const StageConfig& cfg) noexcept {
    const double r_dc = cfg.r_c + cfg.r_e;
    const double v_ceq = cfg.v_cc - cfg.i_cq * r_dc;
    const double r_ac = (cfg.r_c * cfg.r_l) / (cfg.r_c + cfg.r_l);
    const double r_o = (cfg.v_a + v_ceq) / cfg.i_cq;
    
    const double swing_to_sat = v_ceq - cfg.v_ce_sat;
    const double swing_to_cut = cfg.i_cq * r_ac;
    
    const double v_peak_max = std::min(swing_to_sat, swing_to_cut);
    const double v_pp_max = 2.0 * v_peak_max;
    const bool is_clipping_sym = std::abs(swing_to_sat - swing_to_cut) / v_peak_max < 0.05;
    
    return {v_ceq, r_ac, r_o, v_pp_max, is_clipping_sym};
}

int main() {
    constexpr StageConfig cfg{
        .v_cc = 12.0,
        .r_c = 1000.0,
        .r_e = 200.0,
        .r_l = 2000.0,
        .v_a = 100.0,
        .v_ce_sat = 0.2,
        .i_cq = 0.005
    };
    
    constexpr auto res = analyze_bjt_stage(cfg);
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "V_CEQ:     " << res.v_ceq << " V\n";
    std::cout << "r_ac:      " << res.r_ac << " Ohm\n";
    std::cout << "r_o:       " << (res.r_o / 1000.0) << " kOhm\n";
    std::cout << "V_pp(max): " << res.v_pp_max << " V (симетрія: " 
              << (res.is_clipping_sym ? "так" : "ні") << ")\n";
              
    return 0;
}
