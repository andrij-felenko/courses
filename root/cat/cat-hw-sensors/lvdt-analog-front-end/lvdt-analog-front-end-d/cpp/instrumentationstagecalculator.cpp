#include <iostream>
#include <cmath>
#include <iomanip>

class InstrumentationStageCalculator {
public:
    struct Params {
        double carrier_freq_hz;
        double v_diff_max_v;
        double v_target_max_v;
        double opamp_gbp_hz;
        double r_feedback_ohm;
    };

    static void analyze(const Params& p) {
        double g_required = p.v_target_max_v / p.v_diff_max_v;
        double r_gain = (2.0 * p.r_feedback_ohm) / (g_required - 1.0);
        double stage_bw = p.opamp_gbp_hz / g_required;
        double phase_shift_deg = -std::atan(p.carrier_freq_hz / stage_bw) * (180.0 / M_PI);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Параметри підсилювача нормування LVDT ===\n";
        std::cout << "Розрахункове підсилення G: " << g_required << "\n";
        std::cout << "Резистор задання підсилення Rg: " << r_gain << " Ом\n";
        std::cout << "Фазовий зсув на несучій частоті: " << phase_shift_deg << " deg\n";
    }
};
