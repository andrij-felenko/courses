#include <iostream>
#include <iomanip>
#include <expected>
#include <string_view>

namespace embedded::power {

struct PowerSpec {
    float i_sleep_ua{15.0f};           // Струм сну (мкА)
    float t_sleep_s{299.85f};          // Час сну (с)
    float i_sense_ma{12.0f};           // Струм вимірювань (мА)
    float t_sense_ms{100.0f};          // Час вимірювань (мс)
    float i_tx_ma{120.0f};             // Струм передавача (мА)
    float t_tx_ms{50.0f};              // Час передачі (мс)
    float bat_capacity_mah{8500.0f};   // Ємність батареї (мА·год)
    float self_discharge_pct_year{1.5f}; // Саморозряд (%/рік)
    float safety_margin_pct{15.0f};     // Запас (%)
};

struct PowerResult {
    float i_avg_ua{0.0f};
    float battery_life_years{0.0f};
    bool meets_target{false};
};

enum class BudgetError {
    InvalidDuration,
    ZeroCapacity
};

[[nodiscard]] constexpr std::expected<PowerResult, BudgetError>
evaluate_budget(const PowerSpec& spec, float target_years) noexcept {
    const float t_sense_s = spec.t_sense_ms / 1000.0f;
    const float t_tx_s = spec.t_tx_ms / 1000.0f;
    const float t_cycle_s = spec.t_sleep_s + t_sense_s + t_tx_s;

    if (t_cycle_s <= 0.0f) {
        return std::unexpected(BudgetError::InvalidDuration);
    }
    if (spec.bat_capacity_mah <= 0.0f) {
        return std::unexpected(BudgetError::ZeroCapacity);
    }

    const float q_sleep = (spec.i_sleep_ua / 1000.0f) * spec.t_sleep_s;
    const float q_sense = spec.i_sense_ma * t_sense_s;
    const float q_tx    = spec.i_tx_ma * t_tx_s;
    const float q_total = q_sleep + q_sense + q_tx;

    PowerResult res;
    res.i_avg_ua = (q_total / t_cycle_s) * 1000.0f;

    const float usable_cap = spec.bat_capacity_mah * (1.0f - spec.safety_margin_pct / 100.0f);
    const float annual_drain = (res.i_avg_ua / 1000.0f) * 8760.0f +
                               spec.bat_capacity_mah * (spec.self_discharge_pct_year / 100.0f);

    res.battery_life_years = usable_cap / annual_drain;
    res.meets_target = (res.battery_life_years >= target_years);

    return res;
}

} // namespace embedded::power

int main() {
    using namespace embedded::power;

    constexpr PowerSpec itn01_spec{
        .i_sleep_ua = 15.0f,
        .t_sleep_s = 299.85f,
        .i_sense_ma = 12.0f,
        .t_sense_ms = 100.0f,
        .i_tx_ma = 120.0f,
        .t_tx_ms = 50.0f,
        .bat_capacity_mah = 8500.0f,
        .self_discharge_pct_year = 1.5f,
        .safety_margin_pct = 15.0f
    };

    auto res = evaluate_budget(itn01_spec, 5.0f);
    if (!res) {
        std::cerr << "Помилка розрахунку бюджету живлення\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "--- Результати оцінки ТЗ (C++ Power Budget) ---\n";
    std::cout << "Середній струм (I_avg): " << res->i_avg_ua << " мкА\n";
    std::cout << "Час автономної роботи:  " << res->battery_life_years << " років\n";
    std::cout << "Відповідність вимозі:   " << (res->meets_target ? "ПРОЙДЕНО (PASS)" : "НЕ ПРОЙДЕНО (FAIL)") << "\n";

    return 0;
}
