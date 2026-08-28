/*
 * battery_calc.cpp — Об'єктно-орієнтований інженерний калькулятор батареї (C++20)
 */
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <optional>
#include <span>
#include <numbers>

namespace power_calc {

/* Стан робочого циклу мікроконтролера */
struct PowerState {
    std::string name;
    double current_mA{0.0};
    double duration_ms{0.0};
};

/* Специфікація хімічного джерела струму */
struct BatterySpec {
    std::string chemistry_name;
    double nominal_cap_mAh{2400.0};
    double ocv_volts{3.65};
    double ocv_eol_volts{3.30};
    double r_int_room_ohm{3.5};
    double r_int_cold_ohm{32.0};
    double self_discharge_pct_yr{1.0};
    double peukert_k{1.06};
    double max_cont_current_mA{20.0};
};

/* Параметри вбудованої системи */
struct SystemParams {
    double uvlo_cutoff_volts{2.20};
    double design_margin_volts{0.20};
    double operating_temp_c{-15.0};
    double buffer_cap_leakage_uA{0.8};
    double engineering_margin{0.85};
};

/* Структура підсумкових результатів */
struct CalculationResult {
    double cycle_period_s{0.0};
    double charge_per_cycle_uC{0.0};
    double charge_per_cycle_mAh{0.0};
    double average_current_uA{0.0};
    double load_annual_mAh{0.0};
    double self_discharge_annual_mAh{0.0};
    double cap_leakage_annual_mAh{0.0};
    double total_annual_drain_mAh{0.0};
    double peak_current_mA{0.0};
    double peak_duration_ms{0.0};
    double v_drop_raw_volts{0.0};
    double v_min_terminal_volts{0.0};
    bool   uvlo_violation{false};
    bool   buffer_required{false};
    double required_buffer_mF{0.0};
    double derated_usable_cap_mAh{0.0};
    double expected_lifetime_years{0.0};
    double guaranteed_lifetime_years{0.0};
};

/* Калькулятор життєвого циклу */
class BatteryLifeCalculator {
public:
    [[nodiscard]] static std::optional<CalculationResult> calculate(
        std::span<const PowerState> states,
        const BatterySpec& bat,
        const SystemParams& sys) noexcept
    {
        if (states.empty()) {
            return std::nullopt;
        }

        CalculationResult res;
        double total_time_ms = 0.0;
        double total_charge_uC = 0.0;

        for (const auto& state : states) {
            total_time_ms += state.duration_ms;
            total_charge_uC += state.current_mA * state.duration_ms;

            if (state.current_mA > res.peak_current_mA) {
                res.peak_current_mA = state.current_mA;
                res.peak_duration_ms = state.duration_ms;
            }
        }

        res.cycle_period_s = total_time_ms / 1000.0;
        res.charge_per_cycle_uC = total_charge_uC;
        res.charge_per_cycle_mAh = total_charge_uC / 3600.0 / 1000.0;
        res.average_current_uA = total_charge_uC / res.cycle_period_s;

        constexpr double seconds_per_year = 365.25 * 86400.0;
        const double cycles_per_year = seconds_per_year / res.cycle_period_s;
        res.load_annual_mAh = cycles_per_year * res.charge_per_cycle_mAh;

        /* Температурна модель опору */
        double r_effective = bat.r_int_room_ohm;
        if (sys.operating_temp_c < 25.0) {
            const double dt = 25.0 - sys.operating_temp_c;
            r_effective = bat.r_int_room_ohm * std::exp(0.055 * dt);
            if (bat.r_int_cold_ohm > 0.0 && r_effective > bat.r_int_cold_ohm) {
                r_effective = bat.r_int_cold_ohm;
            }
        }

        res.v_drop_raw_volts = (res.peak_current_mA / 1000.0) * r_effective;
        res.v_min_terminal_volts = bat.ocv_eol_volts - res.v_drop_raw_volts;

        const double v_threshold = sys.uvlo_cutoff_volts + sys.design_margin_volts;
        if (res.v_min_terminal_volts < v_threshold || res.peak_current_mA > bat.max_cont_current_mA) {
            res.uvlo_violation = true;
            res.buffer_required = true;

            double delta_v = bat.ocv_eol_volts - sys.uvlo_cutoff_volts - sys.design_margin_volts;
            if (delta_v < 0.1) delta_v = 0.1;

            const double q_pulse_coulombs = (res.peak_current_mA / 1000.0) * (res.peak_duration_ms / 1000.0);
            res.required_buffer_mF = (q_pulse_coulombs / delta_v) * 1000.0;
        }

        /* Саморозряд за Арреніусом */
        double sd_temp_factor = 1.0;
        if (sys.operating_temp_c > 20.0) {
            sd_temp_factor = std::pow(2.0, (sys.operating_temp_c - 20.0) / 10.0);
        }
        res.self_discharge_annual_mAh = bat.nominal_cap_mAh * (bat.self_discharge_pct_yr / 100.0) * sd_temp_factor;

        if (res.buffer_required) {
            res.cap_leakage_annual_mAh = (sys.buffer_cap_leakage_uA / 1000.0) * 8766.0;
        }

        res.total_annual_drain_mAh = res.load_annual_mAh +
                                      res.self_discharge_annual_mAh +
                                      res.cap_leakage_annual_mAh;

        /* Дервейтинг ємності */
        double k_temp = 1.0;
        if (sys.operating_temp_c < 0.0) {
            k_temp = std::max(0.50, 1.0 - (0.0 - sys.operating_temp_c) * 0.012);
        }

        double k_peukert = 0.98;
        if (!res.buffer_required && res.peak_current_mA > 20.0) {
            k_peukert = std::max(0.60, std::pow(2.0 / res.peak_current_mA, bat.peukert_k - 1.0));
        }

        constexpr double k_cutoff = 0.95;
        res.derated_usable_cap_mAh = bat.nominal_cap_mAh * k_temp * k_peukert * k_cutoff;

        if (res.total_annual_drain_mAh > 0.0) {
            res.expected_lifetime_years = res.derated_usable_cap_mAh / res.total_annual_drain_mAh;
            res.guaranteed_lifetime_years = res.expected_lifetime_years * sys.engineering_margin;
        }

        return res;
    }

    static void print_report(const BatterySpec& bat, const SystemParams& sys, const CalculationResult& res) {
        std::cout << "====================================================================\n"
                  << "           ЗВІТ РОЗРАХУНКУ ТЕРМІНУ СЛУЖБИ БАТАРЕЇ (C++20)           \n"
                  << "====================================================================\n"
                  << "Джерело живлення:         " << bat.chemistry_name << " (Номінал: " << bat.nominal_cap_mAh << " мА·год)\n"
                  << "Робоча температура:       " << sys.operating_temp_c << " °C\n"
                  << "Поріг UVLO системи:       " << sys.uvlo_cutoff_volts << " В (Запас: " << sys.design_margin_volts << " В)\n"
                  << "--------------------------------------------------------------------\n"
                  << "ХАРАКТЕРИСТИКИ ПРОФІЛЮ НАВАНТАЖЕННЯ:\n"
                  << "  • Період одного циклу:       " << std::fixed << std::setprecision(2) << res.cycle_period_s << " с\n"
                  << "  • Середній струм споживання: " << std::setprecision(2) << res.average_current_uA << " мкА\n"
                  << "  • Піковий імпульс:           " << res.peak_current_mA << " мА (" << res.peak_duration_ms << " мс)\n"
                  << "--------------------------------------------------------------------\n"
                  << "АНАЛІЗ ПРОСАДКИ НАПРУГИ:\n"
                  << "  • Падіння напруги на R_внутр: " << std::setprecision(3) << res.v_drop_raw_volts << " В\n"
                  << "  • Залишкова напруга шини:    " << res.v_min_terminal_volts << " В\n";

        if (res.uvlo_violation) {
            std::cout << "  [!] ВИЯВЛЕНО НЕБЕЗПЕКУ UVLO: потрібен буферний конденсатор!\n"
                      << "  [+] Мінімальна ємність HLC/EDLC: >= " << std::setprecision(1) << res.required_buffer_mF << " мФ\n";
        } else {
            std::cout << "  [OK] Запас напруги задовільний.\n";
        }

        std::cout << "--------------------------------------------------------------------\n"
                  << "РІЧНИЙ БАЛАНС ЗАРЯДУ:\n"
                  << "  • Споживання навантаження:    " << std::setprecision(2) << res.load_annual_mAh << " мА·год/рік\n"
                  << "  • Саморозряд батареї:         " << res.self_discharge_annual_mAh << " мА·год/рік\n"
                  << "  • Витік конденсатора:         " << res.cap_leakage_annual_mAh << " мА·год/рік\n"
                  << "  • СУМАРНА РІЧНА ВИТРАТА:      " << res.total_annual_drain_mAh << " мА·год/рік\n"
                  << "--------------------------------------------------------------------\n"
                  << "ПІДСУМКОВИЙ ЧАС АВТОНОМНОЇ РОБОТИ:\n"
                  << "  • Корисна ємність (з втратами): " << std::setprecision(0) << res.derated_usable_cap_mAh << " мА·год\n"
                  << "  • Розрахунковий час роботи:     " << std::setprecision(1) << res.expected_lifetime_years << " років\n"
                  << "  • ГАРАНТОВАНИЙ ТЕРМІН СЛУЖБИ:   " << res.guaranteed_lifetime_years << " РОКІВ\n"
                  << "====================================================================\n";
    }
};

} // namespace power_calc

int main() {
    using namespace power_calc;

    const std::vector<PowerState> states = {
        { "Deep Sleep",     0.0025, 59850.0 },
        { "Wake & Sens",    8.0,       50.0 },
        { "Radio TX LoRa", 90.0,       60.0 },
        { "Radio RX Ack",  18.0,       40.0 }
    };

    const BatterySpec battery{
        .chemistry_name = "Li-SOCl2 AA (Bobbin)",
        .nominal_cap_mAh = 2400.0,
        .ocv_volts = 3.65,
        .ocv_eol_volts = 3.30,
        .r_int_room_ohm = 3.5,
        .r_int_cold_ohm = 32.0,
        .self_discharge_pct_yr = 1.0,
        .peukert_k = 1.06,
        .max_cont_current_mA = 20.0
    };

    const SystemParams params{
        .uvlo_cutoff_volts = 2.20,
        .design_margin_volts = 0.20,
        .operating_temp_c = -15.0,
        .buffer_cap_leakage_uA = 0.8,
        .engineering_margin = 0.85
    };

    if (auto res = BatteryLifeCalculator::calculate(states, battery, params)) {
        BatteryLifeCalculator::print_report(battery, params, *res);
    }

    return 0;
}
