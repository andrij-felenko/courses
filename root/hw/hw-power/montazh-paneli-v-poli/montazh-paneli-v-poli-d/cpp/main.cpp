#include <algorithm>

struct SolarFieldPanel {
    double p_stc_w{100.0};       // Номінальна потужність за STC (Вт)
    double gamma_pmp{-0.38};      // Температурний коефіцієнт потужності (%/°C)
    double noct_c{45.0};          // Робоча температура комірки NOCT (°C)
    double soiling_factor{0.05};  // Коефіцієнт втрат від бруду (5%)
};

// Розрахунок реальної польової потужності модуля
[[nodiscard]] constexpr double calculate_field_power(
    const SolarFieldPanel& panel,
    double g_tilt_w_m2,
    double t_ambient_c) noexcept 
{
    if (g_tilt_w_m2 <= 0.0) {
        return 0.0;
    }

    // 1. Оцінка робочої температури кристала
    const double t_cell = t_ambient_c + g_tilt_w_m2 * ((panel.noct_c - 20.0) / 800.0);

    // 2. Вплив температури кристала на вихідну потужність
    const double temp_correction = std::max(0.1, 1.0 + (panel.gamma_pmp / 100.0) * (t_cell - 25.0));

    // 3. Вплив забруднення скла
    const double soiling_correction = std::max(0.0, 1.0 - panel.soiling_factor);

    // 4. Реальна вихідна потужність
    const double p_out = panel.p_stc_w * (g_tilt_w_m2 / 1000.0) * temp_correction * soiling_correction;
    return std::max(0.0, p_out);
}
