#include <iostream>
#include <cmath>
#include <format>
#include <numbers>
#include <algorithm>
#include <string_view>

namespace Reliability {

constexpr double kB_eV = 8.617333262e-5;               // Стала Больцмана (еВ/К)
constexpr double MaxElectrolyticLifeHours = 131400.0; // 15 років стеля
constexpr double HoursPerYear = 8760.0;

// Специфікація конденсатора
struct ElectrolyticCapSpec {
    double l0_hours{5000.0};
    double t_max_c{105.0};
    double dt_max_ripple_c{5.0};
    double v_rated{35.0};
    double i_ripple_rated{2.0};
    double voltage_exponent{1.0};
};

// Робочі умови експлуатації
struct OperatingConditions {
    double t_ambient_c{55.0};
    double v_actual{24.0};
    double i_ripple_actual{1.6};
};

// Звіт розрахунку ресурсу конденсатора
struct CapacitorLifeReport {
    double dt_core_c;
    double t_core_c;
    double raw_life_hours;
    double effective_life_hours;
    double life_years;
    bool is_overheated;
    bool is_clamped_to_15y;
};

// Звіт кваліфікації HTOL
struct HtolReport {
    double equivalent_field_hours;
    double fit_60;
    double fit_90;
    double mtbf_hours_60;
    double mtbf_years_60;
};

// Розрахунок коефіцієнта температурного прискорення Арреніуса
[[nodiscard]] constexpr double arrheniusAccelerationFactor(double ea_ev, double t_use_c, double t_stress_c) noexcept {
    if (ea_ev <= 0.0) return 1.0;
    const double t_use_k = t_use_c + 273.15;
    const double t_stress_k = t_stress_c + 273.15;
    if (t_use_k <= 0.0 || t_stress_k <= 0.0) return 1.0;
    const double inv_diff = (1.0 / t_use_k) - (1.0 / t_stress_k);
    return std::exp((ea_ev / kB_eV) * inv_diff);
}

// Модель Прокоповича-Васкаса для керамічних конденсаторів MLCC
[[nodiscard]] double prokopowiczVaskasFactor(double ea_ev, double t_use_c, double t_stress_c,
                                            double v_use, double v_stress, double n_exponent = 3.0) noexcept {
    const double af_temp = arrheniusAccelerationFactor(ea_ev, t_use_c, t_stress_c);
    double af_volt = 1.0;
    if (v_use > 0.0 && v_stress > 0.0 && n_exponent > 0.0) {
        af_volt = std::pow(v_stress / v_use, n_exponent);
    }
    return af_temp * af_volt;
}

// Розрахунок ресурсу алюмінієвого електролітичного конденсатора
[[nodiscard]] CapacitorLifeReport evaluateCapacitorLife(const ElectrolyticCapSpec& spec,
                                                       const OperatingConditions& op) noexcept {
    double ripple_ratio = (spec.i_ripple_rated > 0.0) ? (op.i_ripple_actual / spec.i_ripple_rated) : 0.0;
    ripple_ratio = std::max(0.0, ripple_ratio);

    const double dt_core = spec.dt_max_ripple_c * (ripple_ratio * ripple_ratio);
    const double t_core = op.t_ambient_c + dt_core;
    const bool overheated = (t_core > spec.t_max_c);

    const double temp_factor = std::pow(2.0, (spec.t_max_c - t_core) / 10.0);

    double volt_factor = 1.0;
    if (spec.voltage_exponent > 0.0 && op.v_actual > 0.0 && op.v_actual <= spec.v_rated) {
        volt_factor = std::pow(spec.v_rated / op.v_actual, spec.voltage_exponent);
    }

    const double raw_life = spec.l0_hours * temp_factor * volt_factor;
    const bool clamped = (raw_life > MaxElectrolyticLifeHours);
    const double final_hours = clamped ? MaxElectrolyticLifeHours : raw_life;

    return CapacitorLifeReport{
        .dt_core_c = dt_core,
        .t_core_c = t_core,
        .raw_life_hours = raw_life,
        .effective_life_hours = final_hours,
        .life_years = final_hours / HoursPerYear,
        .is_overheated = overheated,
        .is_clamped_to_15y = clamped
    };
}

// Розрахунок надійності за тестом HTOL
[[nodiscard]] HtolReport evaluateHtolReliability(int n_samples, double t_test_hours, double af) noexcept {
    const double total_hours = static_cast<double>(n_samples) * t_test_hours * af;
    constexpr double chi2_60 = 1.833; // 60% довіра для r = 0
    constexpr double chi2_90 = 4.605; // 90% довіра для r = 0

    if (total_hours <= 0.0) {
        return HtolReport{0.0, 0.0, 0.0, 0.0, 0.0};
    }

    const double fit60 = (chi2_60 / (2.0 * total_hours)) * 1.0e9;
    const double fit90 = (chi2_90 / (2.0 * total_hours)) * 1.0e9;
    const double mtbf60 = 1.0e9 / fit60;

    return HtolReport{
        .equivalent_field_hours = total_hours,
        .fit_60 = fit60,
        .fit_90 = fit90,
        .mtbf_hours_60 = mtbf60,
        .mtbf_years_60 = mtbf60 / HoursPerYear
    };
}

} // namespace Reliability

int main() {
    using namespace Reliability;
    std::cout << "=================================================================\n";
    std::cout << "     ІНЖЕНЕРНИЙ РОЗРАХУНОК НАДІЙНОСТІ ТА ЗАКОНУ АРРЕНІУСА (C++20) \n";
    std::cout << "=================================================================\n\n";

    // 1. Прискорення для кремнієвого кристала
    constexpr double ea_silicon = 0.70;
    constexpr double t_use = 45.0;
    constexpr double t_stress = 125.0;
    const double af = arrheniusAccelerationFactor(ea_silicon, t_use, t_stress);

    std::cout << std::format("1. ТЕМПЕРАТУРНЕ ПРИСКОРЕННЯ HTOL (КРЕМНІЙ):\n"
                             "   Енергія активації Ea:        {:.2f} еВ\n"
                             "   Робоча температура T_use:    +{:.1f} °C\n"
                             "   Стресова температура T_test: +{:.1f} °C\n"
                             "   -> Коефіцієнт прискорення:   AF = {:.2f} x\n\n",
                             ea_silicon, t_use, t_stress, af);

    // 2. Ресурс електролітичного конденсатора
    const ElectrolyticCapSpec cap_spec{
        .l0_hours = 5000.0,
        .t_max_c = 105.0,
        .dt_max_ripple_c = 5.0,
        .v_rated = 35.0,
        .i_ripple_rated = 2.0,
        .voltage_exponent = 1.0
    };

    const OperatingConditions cap_ops{
        .t_ambient_c = 55.0,
        .v_actual = 24.0,
        .i_ripple_actual = 1.6
    };

    const auto cap_rep = evaluateCapacitorLife(cap_spec, cap_ops);

    std::cout << std::format("2. РЕСУРС ЕЛЕКТРОЛІТИЧНОГО КОНДЕНСАТОРА (105 °C / 5000 год):\n"
                             "   Температура довкілля Ta:     +{:.1f} °C\n"
                             "   Струм пульсацій:             {:.2f} А / {:.2f} А ({:.0f} %)\n"
                             "   Джоулів перегрів серцевини:  Delta T = +{:.2f} °C\n"
                             "   Температура серцевини T_core:+{:.2f} °C\n"
                             "   Розрахунковий ресурс:        {:.0f} годин ({:.2f} років)\n",
                             cap_ops.t_ambient_c, cap_ops.i_ripple_actual, cap_spec.i_ripple_rated,
                             (cap_ops.i_ripple_actual / cap_spec.i_ripple_rated) * 100.0,
                             cap_rep.dt_core_c, cap_rep.t_core_c, cap_rep.effective_life_hours, cap_rep.life_years);
    if (cap_rep.is_clamped_to_15y) {
        std::cout << "   [!] Розрахунок обмежено стелею 15 років через деградацію гумового ущільнювача\n";
    }
    std::cout << "\n";

    // 3. Кваліфікація HTOL
    constexpr int sample_size = 231;
    constexpr double test_duration = 1000.0;
    const auto htol_rep = evaluateHtolReliability(sample_size, test_duration, af);

    std::cout << std::format("3. КВАЛІФІКАЦІЯ ПАРТІЇ ВІС ЗА СТАНДАРТОМ JEDEC HTOL:\n"
                             "   Кількість зразків:           N = {} шт (нуль відмов r = 0)\n"
                             "   Тривалість тесту:            {:.0f} годин (~42 доби)\n"
                             "   Еквівалентний польовий час:  {:.2f} млн приладо-годин\n"
                             "   Інтенсивність відмов (60 %):  lambda = {:.2f} FIT\n"
                             "   Інтенсивність відмов (90 %):  lambda = {:.2f} FIT\n"
                             "   Середній MTBF (60 % довіра):  {:.0f} годин ({:.1f} років)\n"
                             "=================================================================\n",
                             sample_size, test_duration, htol_rep.equivalent_field_hours / 1.0e6,
                             htol_rep.fit_60, htol_rep.fit_90,
                             htol_rep.mtbf_hours_60, htol_rep.mtbf_years_60);

    return 0;
}
