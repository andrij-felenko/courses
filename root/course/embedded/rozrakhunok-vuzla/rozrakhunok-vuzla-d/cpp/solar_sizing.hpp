// solar_sizing.hpp — Ідіоматичний розрахунковий модуль на C++20
#pragma once
#include <string_view>
#include <expected>
#include <cmath>
#include <format>

namespace power::solar {

enum class SizingError {
    kInvalidVoltages,
    kInvalidTimeIntervals,
    kZeroSolarIrradiance,
    kInvalidEfficiencyRange
};

struct NodeProfile {
    double bus_voltage_v       = 3.3;   // Напруга цифрової шини, В
    double sleep_current_ma    = 0.045; // Струм сну, мА (45 мкА)
    double sleep_duration_s    = 58.0;  // Час сну, с
    double active_current_ma   = 15.0;  // Струм датчиків, мА
    double active_duration_s   = 1.0;   // Час вимірювання, с
    double tx_current_ma       = 180.0; // Струм передачі, мА
    double tx_duration_s       = 1.0;   // Час передачі, с
    double conv_efficiency     = 0.90;  // ККД DC-DC бака
    double bms_dark_current_ua = 75.0;  // Сумарний витік (BMS + темновий контролера), мкА
};

struct SizingConstraints {
    double autonomy_days       = 5.0;   // Число діб без сонця (N_autonomy)
    double recovery_days       = 4.0;   // Доби на відновлення (N_recovery)
    double worst_psh           = 1.10;  // Грудневий PSH, год/доба
    double batt_nominal_v      = 12.8;  // Номінальна напруга батареї, В (4S LiFePO4)
    double max_dod             = 0.80;  // Гранична глибина розряду (80% для LFP)
    double batt_coulombic_eff  = 0.95;  // Ефективність заряду АКБ
    double temp_capacity_coeff = 0.75;  // Делейтинг ємності при -15 °C
    bool   use_mppt            = true;  // Тип контролера: true = MPPT, false = PWM
};

struct SizingResult {
    double e_day_wh;            // Добовий бюджет, Вт·год/доба
    double p_avg_mw;            // Середня потужність, мВт
    double batt_energy_nom_wh;  // Номінальна енергія АКБ, Вт·год
    double batt_capacity_ah;    // Ємність АКБ, А·год
    double pv_power_required_w; // Необхідна потужність панелі STC, Вт_пік
    double system_efficiency;   // Підсумковий ККД тракту
};

[[nodiscard]] constexpr auto calculate_system(const NodeProfile& node,
                                              const SizingConstraints& env)
    -> std::expected<SizingResult, SizingError>
{
    if (node.bus_voltage_v <= 0.0 || env.batt_nominal_v <= 0.0) {
        return std::unexpected(SizingError::kInvalidVoltages);
    }
    if (node.conv_efficiency <= 0.0 || node.conv_efficiency > 1.0 ||
        env.max_dod <= 0.0 || env.max_dod > 1.0) {
        return std::unexpected(SizingError::kInvalidEfficiencyRange);
    }
    if (env.worst_psh <= 0.0) {
        return std::unexpected(SizingError::kZeroSolarIrradiance);
    }

    const double t_cycle = node.sleep_duration_s + node.active_duration_s + node.tx_duration_s;
    if (t_cycle <= 0.0) {
        return std::unexpected(SizingError::kInvalidTimeIntervals);
    }

    // 1. Інтегрування енергії робочого циклу
    const double e_sleep_j = node.bus_voltage_v * (node.sleep_current_ma * 1e-3) * node.sleep_duration_s;
    const double e_act_j   = node.bus_voltage_v * (node.active_current_ma * 1e-3) * node.active_duration_s;
    const double e_tx_j    = node.bus_voltage_v * (node.tx_current_ma * 1e-3) * node.tx_duration_s;
    const double e_cycle_j = e_sleep_j + e_act_j + e_tx_j;

    const double cycles_per_day = 86400.0 / t_cycle;
    const double e_load_day_wh  = (cycles_per_day * e_cycle_j) / 3600.0;

    const double e_leak_day_wh = env.batt_nominal_v * (node.bms_dark_current_ua * 1e-6) * 24.0;
    const double e_day_gross   = (e_load_day_wh / node.conv_efficiency) + e_leak_day_wh;
    const double e_day_wh      = e_day_gross * 1.0005; // Врахування саморозряду LFP
    const double p_avg_mw      = (e_day_wh / 24.0) * 1000.0;

    // 2. Розрахунок акумуляторного блоку
    const double denom_batt = env.max_dod * env.batt_coulombic_eff * env.temp_capacity_coeff;
    const double batt_energy_nom_wh = (e_day_wh * env.autonomy_days) / denom_batt;
    const double batt_capacity_ah   = batt_energy_nom_wh / env.batt_nominal_v;

    // 3. Розрахунок сонячного поля з урахуванням делейтингу
    const double eta_ctrl    = env.use_mppt ? 0.96 : 0.65;
    constexpr double kEtaDirt = 0.94;
    constexpr double kEtaSnow = 0.92;
    constexpr double kEtaWire = 0.99;
    constexpr double kEtaTemp = 1.11; // Зимовий температурний виграш

    const double sys_eff = eta_ctrl * kEtaDirt * kEtaSnow * kEtaWire * kEtaTemp;
    const double recovery_factor = 1.0 + (env.autonomy_days / (env.recovery_days * env.batt_coulombic_eff));
    const double pv_power_w = (e_day_wh / (env.worst_psh * sys_eff)) * recovery_factor;

    return SizingResult{
        .e_day_wh            = e_day_wh,
        .p_avg_mw            = p_avg_mw,
        .batt_energy_nom_wh  = batt_energy_nom_wh,
        .batt_capacity_ah    = batt_capacity_ah,
        .pv_power_required_w = pv_power_w,
        .system_efficiency   = sys_eff
    };
}

} // namespace power::solar
