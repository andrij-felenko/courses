#include <iostream>
#include <iomanip>
#include <string_view>

struct TvsDevice {
    double v_rwm{3.3};       // Робоча зворотна напруга, В
    double v_br{5.0};        // Напруга пробою, В
    double v_hold{3.5};      // Напруга утримання (snapback), В
    double r_dyn{0.22};      // Динамічний опір, Ом
    double c_j{0.35};        // Паразитна ємність, пФ
    bool is_snapback{true};  // Прапорець структури snapback
    double l_trace_nh{1.5};  // Паразитна індуктивність доріжки, нГн
};

struct SimulationResult {
    double v_clamp_peak{0.0};
    double v_clamp_30ns{0.0};
    double v_inductive{0.0};
    bool is_safe_for_ic{false};
};

[[nodiscard]] constexpr SimulationResult evaluate_esd_protection(
    const TvsDevice& tvs, double v_esd_kv, double v_max_ic) noexcept 
{
    const double i_peak = v_esd_kv * 3.75;
    const double di_dt = i_peak / 0.8; // Швидкість наростання, А/нс
    const double i_30ns = v_esd_kv * 2.0;

    const double v_inductive = (tvs.l_trace_nh * 1e-9) * (di_dt * 1e9);
    const double v_base = tvs.is_snapback ? tvs.v_hold : tvs.v_br;
    const double v_tvs_peak = v_base + (i_peak * tvs.r_dyn);

    const double v_clamp_peak = v_tvs_peak + v_inductive;
    const double v_clamp_30ns = v_base + (i_30ns * tvs.r_dyn);

    return SimulationResult{
        .v_clamp_peak = v_clamp_peak,
        .v_clamp_30ns = v_clamp_30ns,
        .v_inductive = v_inductive,
        .is_safe_for_ic = (v_clamp_peak < v_max_ic)
    };
}

int main() {
    constexpr TvsDevice tvs{
        .v_rwm = 3.3,
        .v_br = 5.0,
        .v_hold = 3.5,
        .r_dyn = 0.22,
        .c_j = 0.35,
        .is_snapback = true,
        .l_trace_nh = 1.5
    };

    constexpr double v_esd = 8.0;     // 8 кВ IEC 61000-4-2
    constexpr double v_ic_max = 12.0; // Максимально допустима напруга на IC

    const auto r = evaluate_esd_protection(tvs, v_esd, v_ic_max);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Результати моделювання захисту при 8 кВ IEC 61000-4-2:\n";
    std::cout << "• Піковий струм розряду: " << (v_esd * 3.75) << " A\n";
    std::cout << "• Індуктивний стрибок напруги: " << r.v_inductive << " B\n";
    std::cout << "• Пікова напруга на вході IC: " << r.v_clamp_peak << " B\n";
    std::cout << "• Залишкова напруга на 30 нс: " << r.v_clamp_30ns << " B\n";
    std::cout << "• Статус захисту: " << (r.is_safe_for_ic ? "БЕЗПЕЧНО" : "НЕБЕЗПЕКА ПРОБОЮ") << '\n';

    return 0;
}
