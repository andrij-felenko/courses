#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>
#include <expected>
#include <algorithm>

namespace power_analysis {

constexpr double KB_EV = 8.617333262e-5;
constexpr double T_REF_K = 85.0 + 273.15;

enum class CapType {
    NiobiumOxide,
    TantalumMno2
};

struct CapacitorSpec {
    CapType type;
    std::string_view part_number;
    double capacitance_uf;
    double rated_voltage_v;
    double esr_ohm;
    double r_th_c_per_w;
    double base_fit;
};

struct CircuitCondition {
    double bus_voltage_v;
    double ripple_current_a;
    double source_res_ohm;
    double loop_inductance_nh;
    double operating_temp_c;
};

struct AnalysisResult {
    double inrush_peak_current_a;
    double didt_max_a_per_us;
    double damping_factor;
    double power_loss_w;
    double temp_rise_c;
    double allowed_voltage_v;
    bool is_derating_valid;
    bool is_thermal_valid;
    double operating_fit;
    double mtbf_years;
    std::string_view safety_status;
};

enum class AnalysisError {
    InvalidParameters,
    TemperatureOutOfRange
};

[[nodiscard]] constexpr std::expected<AnalysisResult, AnalysisError> evaluate_capacitor(
    const CapacitorSpec& cap,
    const CircuitCondition& cond) noexcept
{
    if (cap.rated_voltage_v <= 0.0 || cond.bus_voltage_v <= 0.0 || cap.capacitance_uf <= 0.0) {
        return std::unexpected(AnalysisError::InvalidParameters);
    }
    if (cond.operating_temp_c < -55.0 || cond.operating_temp_c > 150.0) {
        return std::unexpected(AnalysisError::TemperatureOutOfRange);
    }

    AnalysisResult res{};

    // 1. Динаміка пускового струму та коефіцієнт демпфування
    const double total_r = std::max(1e-4, cond.source_res_ohm + cap.esr_ohm);
    res.inrush_peak_current_a = cond.bus_voltage_v / total_r;

    const double loop_l_h = cond.loop_inductance_nh * 1e-9;
    const double cap_f = cap.capacitance_uf * 1e-6;

    if (loop_l_h > 1e-12) {
        res.didt_max_a_per_us = (cond.bus_voltage_v / loop_l_h) * 1e-6;
        res.damping_factor = (total_r / 2.0) * std::sqrt(cap_f / loop_l_h);
    } else {
        res.didt_max_a_per_us = 0.0;
        res.damping_factor = 10.0;
    }

    // 2. Втрати потужності та тепловий баланс
    res.power_loss_w = (cond.ripple_current_a * cond.ripple_current_a) * cap.esr_ohm;
    res.temp_rise_c = res.power_loss_w * cap.r_th_c_per_w;
    res.is_thermal_valid = (res.temp_rise_c <= 10.0);

    // 3. Дератинг напруги з урахуванням власного перегріву
    const double t_effective = cond.operating_temp_c + res.temp_rise_c;

    if (cap.type == CapType::NiobiumOxide) {
        if (t_effective <= 85.0) {
            res.allowed_voltage_v = cap.rated_voltage_v * 0.80;
        } else if (t_effective <= 125.0) {
            const double factor = 0.80 - 0.30 * ((t_effective - 85.0) / 40.0);
            res.allowed_voltage_v = cap.rated_voltage_v * factor;
        } else {
            res.allowed_voltage_v = 0.0;
        }
    } else { // TantalumMno2
        if (t_effective <= 85.0) {
            res.allowed_voltage_v = cap.rated_voltage_v * 0.50;
        } else if (t_effective <= 125.0) {
            const double factor = 0.50 - 0.17 * ((t_effective - 85.0) / 40.0);
            res.allowed_voltage_v = cap.rated_voltage_v * factor;
        } else {
            res.allowed_voltage_v = 0.0;
        }
    }

    res.is_derating_valid = (cond.bus_voltage_v <= res.allowed_voltage_v);

    // 4. Оцінка надійності: FIT та MTBF
    const double v_ratio = std::clamp(cond.bus_voltage_v / cap.rated_voltage_v, 0.0, 1.2);
    const double n_exp = (cap.type == CapType::NiobiumOxide) ? 3.5 : 14.0;
    const double af_v = std::pow(v_ratio, n_exp);

    const double t_op_k = t_effective + 273.15;
    constexpr double ea_ev = 0.15;
    const double delta_inv_t = (1.0 / T_REF_K) - (1.0 / t_op_k);
    const double af_t = std::exp((ea_ev / KB_EV) * delta_inv_t);

    res.operating_fit = cap.base_fit * af_v * af_t;
    res.mtbf_years = (res.operating_fit > 0.0) ? ((1.0e9 / res.operating_fit) / 8760.0) : 0.0;

    if (!res.is_derating_valid) {
        res.safety_status = (cap.type == CapType::NiobiumOxide)
            ? "ПОПЕРЕДЖЕННЯ: дератинг перевищено (відмова без горіння)"
            : "КРИТИЧНА ПОМИЛКА: ризик спалаху танталу через перевищення дератингу 50%!";
    } else if (!res.is_thermal_valid) {
        res.safety_status = "УВАГА: перегрів від пульсацій струму перевищує норму (+10 °C)";
    } else {
        res.safety_status = "НОРМА: робоча зона безпечна";
    }

    return res;
}

} // namespace power_analysis

int main() {
    using namespace power_analysis;

    constexpr CapacitorSpec nbo_cap{
        .type = CapType::NiobiumOxide,
        .part_number = "NOJB107M006R0200 (AVX 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.200,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    constexpr CapacitorSpec ta_cap{
        .type = CapType::TantalumMno2,
        .part_number = "TAJB107M006RNJ (KEMET 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.250,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    constexpr CircuitCondition bus_5v{
        .bus_voltage_v = 5.0,
        .ripple_current_a = 0.450,
        .source_res_ohm = 0.030,
        .loop_inductance_nh = 15.0,
        .operating_temp_c = 65.0
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=================================================================\n";
    std::cout << "ПОРІВНЯЛЬНИЙ АНАЛІЗ ПОВЕДІНКИ NbO ТА Ta-MnO2 НА ШИНІ 5.0 В\n";
    std::cout << "=================================================================\n\n";

    if (auto res = evaluate_capacitor(nbo_cap, bus_5v); res.has_value()) {
        std::cout << "1. " << nbo_cap.part_number << '\n';
        std::cout << "   Пусковий струм I_peak: " << res->inrush_peak_current_a << " А, dI/dt: "
                  << res->didt_max_a_per_us << " А/мкс, Демпфування zeta: " << res->damping_factor << '\n';
        std::cout << "   Перегрів від пульсацій: +" << res->temp_rise_c << " °C\n";
        std::cout << "   Дозволена напруга: " << res->allowed_voltage_v << " В -> "
                  << (res->is_derating_valid ? "ПРОХОДИТЬ (20% дератинг)" : "ЗАБОРОНЕНО") << '\n';
        std::cout << "   FIT: " << res->operating_fit << " | MTBF: " << res->mtbf_years << " років\n";
        std::cout << "   Статус: " << res->safety_status << "\n\n";
    }

    if (auto res = evaluate_capacitor(ta_cap, bus_5v); res.has_value()) {
        std::cout << "2. " << ta_cap.part_number << '\n';
        std::cout << "   Пусковий струм I_peak: " << res->inrush_peak_current_a << " А, dI/dt: "
                  << res->didt_max_a_per_us << " А/мкс, Демпфування zeta: " << res->damping_factor << '\n';
        std::cout << "   Перегрів від пульсацій: +" << res->temp_rise_c << " °C\n";
        std::cout << "   Дозволена напруга: " << res->allowed_voltage_v << " В -> "
                  << (res->is_derating_valid ? "ПРОХОДИТЬ" : "НЕ ПРОХОДИТЬ (потрібно 50%)") << '\n';
        std::cout << "   FIT: " << res->operating_fit << " | MTBF: " << res->mtbf_years << " років\n";
        std::cout << "   Статус: " << res->safety_status << "\n";
    }

    return 0;
}
