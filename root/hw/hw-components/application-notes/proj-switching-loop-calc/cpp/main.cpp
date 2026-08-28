#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <algorithm>
#include <expected>
#include <string_view>

/* Вхідна специфікація перетворювача */
struct BuckSpec {
    double v_in{12.0};            // Вхідна напруга, В
    double v_out{3.3};            // Вихідна напруга, В
    double i_out{4.0};            // Максимальний струм, А
    double f_sw{500'000.0};       // Частота комутації, Гц
    double l_ind{2.2e-6};         // Індуктивність дроселя, Гн
    double c_out_nom{66.0e-6};    // Номінальна ємність, Ф
    double esr{0.003};            // Еквівалентний послідовний опір ESR, Ом
    double v_ref{0.8};            // Внутрішня опора підсилювача помилки, В
    double v_ramp{1.2};           // Амплітуда генератора пилки ШІМ, В
    double dc_bias_factor{0.65};  // Коефіцієнт дератингу MLCC від постійної напруги
};

/* Результати синтезу кіл компенсації */
struct Type3Result {
    double f_0{};                 // Власний резонанс LC, Гц
    double f_z_esr{};             // Нуль вихідного конденсатора, Гц
    double f_c{};                 // Частота зрізу контуру, Гц
    double r1{10'000.0};          // Верхній резистор зворотного зв'язку, Ом
    double r_bot{};               // Нижній резистор дільника вихідної напруги, Ом
    double r2{};                  // Резистор підсилення інтегратора, Ом
    double r3{};                  // Резистор диференціюючої ланки, Ом
    double c1{};                  // Конденсатор високочастотного полюса, Ф
    double c2{};                  // Конденсатор інтегруючої ланки, Ф
    double c3{};                  // Конденсатор фазового випередження, Ф
    double phase_margin_deg{};    // Запас фази петлі, градуси
    bool is_stable{false};        // Оцінка стійкості (PM >= 45°)
};

enum class CalcError {
    InvalidFrequency,
    InvalidInductance,
    InvalidCapacitance,
    ZeroVoltage
};

/* Округлення до стандартного номіналу ряду E24 */
constexpr double round_to_e24(double val) noexcept {
    if (val <= 0.0) return 0.0;
    constexpr std::array<double, 24> e24_table = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };
    const double exponent = std::floor(std::log10(val));
    const double mantissa = val / std::pow(10.0, exponent);

    auto it = std::min_element(e24_table.begin(), e24_table.end(),
        [mantissa](double a, double b) {
            return std::abs(mantissa - a) < std::abs(mantissa - b);
        });

    return (*it) * std::pow(10.0, exponent);
}

/* Синтез Type III компенсатора за правилами Application Note */
[[nodiscard]] constexpr std::expected<Type3Result, CalcError>
synthesize_type3(const BuckSpec& spec) noexcept {
    if (spec.f_sw <= 0.0) return std::unexpected(CalcError::InvalidFrequency);
    if (spec.l_ind <= 0.0) return std::unexpected(CalcError::InvalidInductance);
    if (spec.c_out_nom <= 0.0) return std::unexpected(CalcError::InvalidCapacitance);
    if (spec.v_out <= spec.v_ref) return std::unexpected(CalcError::ZeroVoltage);

    Type3Result res{};
    const double c_eff = spec.c_out_nom * (spec.dc_bias_factor > 0.0 ? spec.dc_bias_factor : 1.0);

    res.f_0 = 1.0 / (2.0 * std::numbers::pi * std::sqrt(spec.l_ind * c_eff));
    res.f_z_esr = 1.0 / (2.0 * std::numbers::pi * spec.esr * c_eff);

    res.f_c = std::min(spec.f_sw / 10.0, spec.f_sw / 5.0);

    const double f_z1 = 0.75 * res.f_0;
    const double f_z2 = res.f_0;
    const double f_p1 = (res.f_z_esr < spec.f_sw * 0.5) ? res.f_z_esr : spec.f_sw * 0.5;
    const double f_p2 = spec.f_sw * 0.5;

    res.r1 = 10'000.0;
    res.r_bot = round_to_e24((res.r1 * spec.v_ref) / (spec.v_out - spec.v_ref));

    const double r2_raw = (spec.v_ramp * res.f_c * f_p1 * res.r1) / (spec.v_in * res.f_0 * res.f_0);
    res.r2 = round_to_e24(r2_raw);

    res.c2 = round_to_e24(1.0 / (2.0 * std::numbers::pi * res.r2 * f_z1));
    res.c1 = round_to_e24(1.0 / (2.0 * std::numbers::pi * res.r2 * f_p1));

    const double r3_raw = res.r1 / ((f_p2 / f_z2) - 1.0);
    res.r3 = round_to_e24(r3_raw);
    res.c3 = round_to_e24(1.0 / (2.0 * std::numbers::pi * (res.r1 + res.r3) * f_z2));

    // Оцінка фазового запасу
    double phi_plant = -180.0 * (std::atan2(res.f_c / res.f_0, 1.0 - std::pow(res.f_c / res.f_0, 2.0)) / std::numbers::pi);
    if (phi_plant > 0.0) phi_plant -= 180.0;
    phi_plant += (std::atan(res.f_c / res.f_z_esr) * 180.0 / std::numbers::pi);

    double phi_comp = -90.0;
    phi_comp += (std::atan(res.f_c / f_z1) * 180.0 / std::numbers::pi);
    phi_comp += (std::atan(res.f_c / f_z2) * 180.0 / std::numbers::pi);
    phi_comp -= (std::atan(res.f_c / f_p1) * 180.0 / std::numbers::pi);
    phi_comp -= (std::atan(res.f_c / f_p2) * 180.0 / std::numbers::pi);

    res.phase_margin_deg = 180.0 + (phi_plant + phi_comp);
    res.is_stable = (res.phase_margin_deg >= 45.0);

    return res;
}

int main() {
    constexpr BuckSpec spec{};
    const auto outcome = synthesize_type3(spec);

    if (!outcome) {
        std::cerr << "Помилка розрахунку параметрів компенсатора!\n";
        return 1;
    }

    const auto& res = *outcome;
    std::cout << "=== Результати розрахунку Type III компенсатора (C++) ===\n"
              << "Резонанс LC фільтра:      f_0   = " << res.f_0 / 1000.0 << " кГц\n"
              << "Нуль ESR кераміки:        f_esr = " << res.f_z_esr / 1000.0 << " кГц\n"
              << "Частота зрізу петлі:      f_c   = " << res.f_c / 1000.0 << " кГц\n"
              << "--------------------------------------------------\n"
              << "R1 = " << res.r1 / 1000.0 << " кОм,  R_bot = " << res.r_bot / 1000.0 << " кОм\n"
              << "R2 = " << res.r2 / 1000.0 << " кОм,  C2 = " << res.c2 * 1e12 << " пФ\n"
              << "C1 = " << res.c1 * 1e12 << " пФ\n"
              << "R3 = " << res.r3 << " Ом,   C3 = " << res.c3 * 1e12 << " пФ\n"
              << "--------------------------------------------------\n"
              << "Очікуваний запас фази:    PM = " << res.phase_margin_deg << "° ("
              << (res.is_stable ? "СТІЙКИЙ" : "НЕСТІЙКИЙ!") << ")\n";

    return 0;
}
