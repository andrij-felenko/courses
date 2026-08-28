#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <format>

struct HotLoopParams {
    double v_in{12.0};        // Вхідна напруга, В
    double i_peak{10.0};      // Піковий струм комутації, А
    double t_sw{2.0e-9};      // Час перемикання, с
    double l_loop_nh{1.1};    // Індуктивність петлі, нГн
    double c_oss_pf{350.0};   // Паразитна ємність транзистора, пФ
    double area_mm2{12.0};    // Площа контуру, мм²
};

struct HotLoopResult {
    double di_dt{0.0};          // А/с
    double v_spike{0.0};        // В
    double v_total_peak{0.0};   // В
    double f_ring_mhz{0.0};     // МГц
    double rel_emi_db{0.0};     // дБ відносно 100 мм²
};

class HotLoopAnalyzer {
public:
    [[nodiscard]] static constexpr HotLoopResult analyze(const HotLoopParams& p) noexcept {
        HotLoopResult res;
        const double l_h = p.l_loop_nh * 1e-9;
        const double c_f = p.c_oss_pf * 1e-12;

        res.di_dt = p.i_peak / p.t_sw;
        res.v_spike = l_h * res.di_dt;
        res.v_total_peak = p.v_in + res.v_spike;

        const double lc = l_h * c_f;
        if (lc > 0.0) {
            res.f_ring_mhz = (1.0 / (2.0 * std::numbers::pi * std::sqrt(lc))) / 1e6;
        }

        if (p.area_mm2 > 0.0) {
            res.rel_emi_db = 20.0 * std::log10(p.area_mm2 / 100.0);
        }

        return res;
    }
};

int main() {
    constexpr HotLoopParams opt{
        .v_in = 12.0,
        .i_peak = 10.0,
        .t_sw = 2.0e-9,
        .l_loop_nh = 1.1,
        .c_oss_pf = 350.0,
        .area_mm2 = 12.0
    };

    const auto r = HotLoopAnalyzer::analyze(opt);

    std::cout << "--- Аналіз оптимізованої гарячої петлі (C++20) ---\n";
    std::cout << "di/dt:           " << std::scientific << r.di_dt << " A/s\n";
    std::cout << "V_spike:         " << std::fixed << r.v_spike << " V\n";
    std::cout << "V_drain_peak:    " << r.v_total_peak << " V\n";
    std::cout << "f_ringing:       " << r.f_ring_mhz << " MHz\n";
    std::cout << "Relative EMI:    " << r.rel_emi_db << " dB\n";

    return 0;
}
