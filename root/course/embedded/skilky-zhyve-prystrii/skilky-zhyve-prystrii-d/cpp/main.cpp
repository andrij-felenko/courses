#include <iostream>
#include <vector>
#include <string_view>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <span>

using namespace std::chrono_literals;

namespace power_estimator {

struct PowerPhase {
    std::string_view name;
    double current_ma;
    std::chrono::milliseconds duration;
};

struct BatterySpec {
    double nominal_capacity_mah;
    double nominal_voltage_v;
    double cutoff_voltage_v;
    double temp_celsius;
    double self_discharge_pct_per_year;
    double peukert_exponent{1.05};
};

struct EstimateResult {
    double total_period_sec;
    double active_charge_mas;
    double sleep_charge_mas;
    double avg_current_ua;
    double self_discharge_ua;
    double effective_capacity_mah;
    double lifetime_days;
    double lifetime_years;
    std::string_view dominant_consumer;
};

class LifetimeEstimator {
public:
    static constexpr double calc_cutoff_factor(double v_nom, double v_cut) noexcept {
        if (v_cut >= v_nom) return 0.05;
        const double headroom = (v_nom - v_cut) / (v_nom - 1.8);
        return std::clamp(headroom, 0.10, 1.00);
    }

    static constexpr double calc_temp_factor(double temp_c) noexcept {
        if (temp_c >= 20.0) return 1.00;
        if (temp_c >= 0.0)  return 0.85 + 0.15 * (temp_c / 20.0);
        if (temp_c >= -20.0) return 0.60 + 0.25 * ((temp_c + 20.0) / 20.0);
        return 0.40;
    }

    static EstimateResult calculate(const BatterySpec& bat, std::span<const PowerPhase> phases) {
        double total_ms = 0.0;
        double active_q = 0.0;
        double sleep_q = 0.0;
        double max_q = 0.0;
        double peak_current = 0.0;
        std::string_view dominant_phase = "Немає активності";

        for (const auto& phase : phases) {
            const double dur_s = std::chrono::duration<double>(phase.duration).count();
            const double q = phase.current_ma * dur_s;
            total_ms += std::chrono::duration<double, std::milli>(phase.duration).count();
            peak_current = std::max(peak_current, phase.current_ma);

            if (phase.current_ma < 0.05) {
                sleep_q += q;
            } else {
                active_q += q;
                if (q > max_q) {
                    max_q = q;
                    dominant_phase = phase.name;
                }
            }
        }

        const double period_sec = total_ms / 1000.0;
        const double avg_load_ma = (active_q + sleep_q) / period_sec;

        // Закон Арреніуса для температурного саморозряду
        const double temp_factor = std::pow(2.0, (bat.temp_celsius - 20.0) / 10.0);
        const double adjusted_self_pct = bat.self_discharge_pct_per_year * temp_factor;
        const double self_discharge_ma = (bat.nominal_capacity_mah * (adjusted_self_pct / 100.0)) / (365.25 * 24.0);

        const double eta_cut = calc_cutoff_factor(bat.nominal_voltage_v, bat.cutoff_voltage_v);
        const double eta_temp = calc_temp_factor(bat.temp_celsius);
        
        double eta_peukert = 1.0;
        if (peak_current > 20.0 && bat.peukert_exponent > 1.01) {
            eta_peukert = std::pow(10.0 / peak_current, bat.peukert_exponent - 1.0);
            eta_peukert = std::clamp(eta_peukert, 0.75, 1.00);
        }

        const double effective_cap = bat.nominal_capacity_mah * eta_cut * eta_temp * eta_peukert;
        const double total_current_ma = avg_load_ma + self_discharge_ma;

        const double hours = effective_cap / total_current_ma;
        const double days = hours / 24.0;
        const double years = days / 365.25;

        std::string_view dominant = dominant_phase;
        if (self_discharge_ma > avg_load_ma) {
            dominant = "Саморозряд батареї";
        }

        return {
            .total_period_sec = period_sec,
            .active_charge_mas = active_q,
            .sleep_charge_mas = sleep_q,
            .avg_current_ua = avg_load_ma * 1000.0,
            .self_discharge_ua = self_discharge_ma * 1000.0,
            .effective_capacity_mah = effective_cap,
            .lifetime_days = days,
            .lifetime_years = years,
            .dominant_consumer = dominant
        };
    }
};

} // namespace power_estimator

int main() {
    using namespace power_estimator;

    constexpr BatterySpec li_socl2{
        .nominal_capacity_mah = 2400.0,
        .nominal_voltage_v = 3.6,
        .cutoff_voltage_v = 2.8,
        .temp_celsius = -10.0,
        .self_discharge_pct_per_year = 1.5,
        .peukert_exponent = 1.08
    };

    const std::vector<PowerPhase> sensor_profile = {
        { "Глибокий сон",        0.006, 59800ms },
        { "Запуск сенсорів I2C", 7.500, 40ms },
        { "Передача LoRa TX",    48.000, 140ms },
        { "Запис Flash EEPROM",  5.000, 20ms }
    };

    const auto res = LifetimeEstimator::calculate(li_socl2, sensor_profile);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "================ ЗВІТ АВТОНОМНОСТІ ВУЗЛА (C++20) ================\n";
    std::cout << "Період циклу:                " << res.total_period_sec << " с\n";
    std::cout << "Заряд активної частини:      " << res.active_charge_mas << " мА·с\n";
    std::cout << "Заряд фази сну:              " << res.sleep_charge_mas << " мА·с\n";
    std::cout << "Середній струм навантаження:  " << res.avg_current_ua << " мкА\n";
    std::cout << "Струм саморозряду комірки:   " << res.self_discharge_ua << " мкА\n";
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << "Ефективна доступна ємність:  " << res.effective_capacity_mah << " мА·год ("
              << (res.effective_capacity_mah / li_socl2.nominal_capacity_mah * 100.0) << " % номіналу)\n";
    std::cout << "Прогнозована автономність:   " << res.lifetime_days << " діб ("
              << res.lifetime_years << " років)\n";
    std::cout << "Головний споживач енергії:   " << res.dominant_consumer << "\n";
    std::cout << "=================================================================\n";

    return 0;
}
