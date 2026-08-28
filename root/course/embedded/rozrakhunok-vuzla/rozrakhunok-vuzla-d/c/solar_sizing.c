/* solar_sizing.h / solar_sizing.c — Інженерний калькулятор сонячного живлення */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double bus_voltage_v;       /* Напруга цифрової шини, В (напр. 3.3) */
    double sleep_current_ma;    /* Струм глибокого сну, мА */
    double sleep_duration_s;    /* Тривалість сну в циклі, с */
    double active_current_ma;   /* Струм вимірювання, мА */
    double active_duration_s;   /* Тривалість вимірювання, с */
    double tx_current_ma;       /* Струм передавача, мА */
    double tx_duration_s;       /* Тривалість передачі, с */
    double conv_efficiency;     /* ККД стабілізатора плати (напр. 0.90) */
    double bms_dark_current_ua; /* Сумарний струм BMS і витоку MPPT, мкА */
} NodeProfile;

typedef struct {
    double autonomy_days;       /* Число діб без сонця (N_autonomy, напр. 5.0) */
    double recovery_days;       /* Доби на відновлення заряду (N_recovery, напр. 4.0) */
    double worst_psh;           /* Зимовий мінімум інсоляції, год (напр. 1.10) */
    double batt_nominal_v;      /* Номінальна напруга АКБ, В (12.8 для 4S LFP) */
    double max_dod;             /* Граничний DoD (0.80 для LiFePO4) */
    double batt_coulombic_eff;  /* ККД заряду батареї (0.95) */
    double temp_capacity_coeff; /* Температурний делейтинг АКБ (0.75 для -15°C) */
    bool   use_mppt;            /* true = MPPT (96%), false = PWM (65%) */
} SizingConstraints;

typedef struct {
    double e_day_wh;            /* Повне добове споживання, Вт·год/доба */
    double p_avg_mw;            /* Середня споживана потужність, мВт */
    double batt_energy_nom_wh;  /* Необхідний запас енергії АКБ, Вт·год */
    double batt_capacity_ah;    /* Необхідна ємність АКБ, А·год */
    double pv_power_required_w; /* Необхідна потужність панелі STC, Вт_пік */
    double system_efficiency;   /* Результуючий ККД тракту генерації */
} SizingResult;

bool calculate_solar_system(const NodeProfile *node,
                            const SizingConstraints *env,
                            SizingResult *res)
{
    if (!node || !env || !res) return false;
    if (node->conv_efficiency <= 0.0 || env->worst_psh <= 0.0 || env->batt_nominal_v <= 0.0)
        return false;

    /* 1. Енергія одного робочого циклу (в Джоулях) */
    double e_sleep_j = node->bus_voltage_v * (node->sleep_current_ma * 1e-3) * node->sleep_duration_s;
    double e_act_j   = node->bus_voltage_v * (node->active_current_ma * 1e-3) * node->active_duration_s;
    double e_tx_j    = node->bus_voltage_v * (node->tx_current_ma * 1e-3) * node->tx_duration_s;
    double e_cycle_j = e_sleep_j + e_act_j + e_tx_j;

    double t_cycle_s = node->sleep_duration_s + node->active_duration_s + node->tx_duration_s;
    if (t_cycle_s <= 0.0) return false;

    double cycles_per_day = 86400.0 / t_cycle_s;
    double e_load_day_wh  = (cycles_per_day * e_cycle_j) / 3600.0;

    /* Додавання втрат стабілізатора та постійних витоків */
    double e_leak_day_wh = env->batt_nominal_v * (node->bms_dark_current_ua * 1e-6) * 24.0;
    double e_day_gross   = (e_load_day_wh / node->conv_efficiency) + e_leak_day_wh;
    res->e_day_wh        = e_day_gross * 1.0005; /* +0.05% саморозряд на добу */
    res->p_avg_mw        = (res->e_day_wh / 24.0) * 1000.0;

    /* 2. Розрахунок акумулятора */
    double denom_batt = env->max_dod * env->batt_coulombic_eff * env->temp_capacity_coeff;
    if (denom_batt <= 0.0) return false;

    res->batt_energy_nom_wh = (res->e_day_wh * env->autonomy_days) / denom_batt;
    res->batt_capacity_ah   = res->batt_energy_nom_wh / env->batt_nominal_v;

    /* 3. Розрахунок сонячного модуля */
    double eta_ctrl = env->use_mppt ? 0.96 : 0.65;
    double eta_dirt = 0.94;
    double eta_snow = 0.92;
    double eta_wire = 0.99;
    double eta_temp_pv = 1.11; /* Зимовий приріст напруги Voc/Vmp */

    res->system_efficiency = eta_ctrl * eta_dirt * eta_snow * eta_wire * eta_temp_pv;

    double recovery_factor = 1.0 + (env->autonomy_days / (env->recovery_days * env->batt_coulombic_eff));
    res->pv_power_required_w = (res->e_day_wh / (env->worst_psh * res->system_efficiency)) * recovery_factor;

    return true;
}
