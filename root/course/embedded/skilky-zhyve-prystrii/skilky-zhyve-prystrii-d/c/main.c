#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Структура опису фази споживання */
typedef struct {
    const char *name;       /* Назва фази */
    double current_ma;      /* Струм споживання (мА) */
    double duration_ms;     /* Тривалість фази (мс) */
} PowerPhase;

/* Параметри батареї та умов експлуатації */
typedef struct {
    double nominal_capacity_mah;  /* Номінальна ємність (мА·год) */
    double nominal_voltage_v;     /* Номінальна напруга (В) */
    double cutoff_voltage_v;      /* Напруга відсічки пристрою (В) */
    double temp_celsius;          /* Робоча температура (°C) */
    double self_discharge_pct_yr; /* Річний саморозряд (%/рік за 20°C) */
    double peukert_exponent;      /* Експонента Пейкерта (1.05 - 1.25) */
} BatterySpec;

/* Результати розрахунку */
typedef struct {
    double total_period_sec;      /* Загальний період циклу (с) */
    double active_charge_mas;     /* Заряд активних фаз (мА·с) */
    double sleep_charge_mas;      /* Заряд фази сну (мА·с) */
    double cycle_charge_mas;      /* Повний заряд циклу (мА·с) */
    double avg_current_ma;        /* Середній струм навантаження (мА) */
    double self_discharge_ma;     /* Еквівалентний струм саморозряду (мА) */
    double total_effective_ma;    /* Повний ефективний струм (мА) */
    double effective_capacity_mah;/* Фактично доступна ємність (мА·год) */
    double lifetime_hours;        /* Час життя в годинах */
    double lifetime_days;         /* Час життя в днях */
    double lifetime_years;        /* Час життя в роках */
    const char *dominant_factor;  /* Головний споживач енергії */
} BatteryEstimate;

/* Розрахунок дератингу ємності за напругою відсічки */
static double calc_cutoff_factor(double v_nom, double v_cut) {
    if (v_cut >= v_nom) return 0.05;
    double headroom = (v_nom - v_cut) / (v_nom - 1.8);
    if (headroom > 1.0) headroom = 1.0;
    if (headroom < 0.1) headroom = 0.1;
    return headroom;
}

/* Розрахунок температурного фактора */
static double calc_temp_factor(double temp_c) {
    if (temp_c >= 20.0) {
        return 1.0;
    } else if (temp_c >= 0.0) {
        return 0.85 + 0.15 * (temp_c / 20.0);
    } else if (temp_c >= -20.0) {
        return 0.60 + 0.25 * ((temp_c + 20.0) / 20.0);
    } else {
        return 0.40;
    }
}

/* Головна функція розрахунку автономності */
bool estimate_battery_lifetime(
    const BatterySpec *bat,
    const PowerPhase *phases,
    size_t num_phases,
    BatteryEstimate *out_est
) {
    if (!bat || !phases || num_phases == 0 || !out_est) return false;

    double period_ms = 0.0;
    double active_charge = 0.0;
    double sleep_charge = 0.0;
    double max_phase_charge = 0.0;
    const char *dominant_phase = "Невизначено";
    double peak_current_ma = 0.0;

    for (size_t i = 0; i < num_phases; ++i) {
        double phase_q = phases[i].current_ma * (phases[i].duration_ms / 1000.0);
        period_ms += phases[i].duration_ms;

        if (phases[i].current_ma > peak_current_ma) {
            peak_current_ma = phases[i].current_ma;
        }

        /* Умовно вважаємо струми < 0.05 мА фазою сну */
        if (phases[i].current_ma < 0.05) {
            sleep_charge += phase_q;
        } else {
            active_charge += phase_q;
            if (phase_q > max_phase_charge) {
                max_phase_charge = phase_q;
                dominant_phase = phases[i].name;
            }
        }
    }

    if (period_ms <= 0.0) return false;

    out_est->total_period_sec = period_ms / 1000.0;
    out_est->active_charge_mas = active_charge;
    out_est->sleep_charge_mas = sleep_charge;
    out_est->cycle_charge_mas = active_charge + sleep_charge;
    out_est->avg_current_ma = out_est->cycle_charge_mas / out_est->total_period_sec;

    /* Розрахунок саморозряду з урахуванням температури (правило Арреніуса) */
    double temp_accel = pow(2.0, (bat->temp_celsius - 20.0) / 10.0);
    double adjusted_self_pct = bat->self_discharge_pct_yr * temp_accel;
    out_est->self_discharge_ma = (bat->nominal_capacity_mah * (adjusted_self_pct / 100.0)) / (365.25 * 24.0);

    out_est->total_effective_ma = out_est->avg_current_ma + out_est->self_discharge_ma;

    /* Коригування ємності */
    double eta_cut = calc_cutoff_factor(bat->nominal_voltage_v, bat->cutoff_voltage_v);
    double eta_temp = calc_temp_factor(bat->temp_celsius);
    
    /* Деградація Пейкерта від імпульсів */
    double eta_peukert = 1.0;
    if (peak_current_ma > 20.0 && bat->peukert_exponent > 1.01) {
        eta_peukert = pow(10.0 / peak_current_ma, bat->peukert_exponent - 1.0);
        if (eta_peukert > 1.0) eta_peukert = 1.0;
        if (eta_peukert < 0.75) eta_peukert = 0.75;
    }

    out_est->effective_capacity_mah = bat->nominal_capacity_mah * eta_cut * eta_temp * eta_peukert;

    out_est->lifetime_hours = out_est->effective_capacity_mah / out_est->total_effective_ma;
    out_est->lifetime_days = out_est->lifetime_hours / 24.0;
    out_est->lifetime_years = out_est->lifetime_days / 365.25;

    if (out_est->self_discharge_ma > out_est->avg_current_ma) {
        out_est->dominant_factor = "Саморозряд батареї";
    } else {
        out_est->dominant_factor = dominant_phase;
    }

    return true;
}

int main(void) {
    BatterySpec cell = {
        .nominal_capacity_mah = 2400.0,
        .nominal_voltage_v = 3.6,
        .cutoff_voltage_v = 2.8,
        .temp_celsius = -10.0,
        .self_discharge_pct_yr = 1.5,
        .peukert_exponent = 1.08
    };

    PowerPhase cycle[] = {
        { .name = "Глибокий сон",        .current_ma = 0.006, .duration_ms = 59800.0 },
        { .name = "Запуск сенсорів I2C", .current_ma = 7.5,   .duration_ms = 40.0 },
        { .name = "Передача LoRa TX",    .current_ma = 48.0,  .duration_ms = 140.0 },
        { .name = "Запис Flash EEPROM",  .current_ma = 5.0,   .duration_ms = 20.0 }
    };

    BatteryEstimate result;
    if (estimate_battery_lifetime(&cell, cycle, sizeof(cycle)/sizeof(cycle[0]), &result)) {
        printf("================ ЗВІТ АВТОНОМНОСТІ ВУЗЛА ================\n");
        printf("Період циклу:               %.1f с\n", result.total_period_sec);
        printf("Заряд активних фаз:         %.3f мА·с\n", result.active_charge_mas);
        printf("Заряд фази сну:             %.3f мА·с\n", result.sleep_charge_mas);
        printf("Середній струм навантаження: %.2f мкА\n", result.avg_current_ma * 1000.0);
        printf("Струм саморозряду (T=%.0f°C): %.2f мкА\n", cell.temp_celsius, result.self_discharge_ma * 1000.0);
        printf("---------------------------------------------------------\n");
        printf("Доступна ємність (C_eff):   %.1f мА·год (з %.0f мА·год)\n", 
               result.effective_capacity_mah, cell.nominal_capacity_mah);
        printf("Оцінка часу автономності:   %.1f діб (%.2f років)\n", 
               result.lifetime_days, result.lifetime_years);
        printf("Головний чинник витрат:     %s\n", result.dominant_factor);
        printf("=========================================================\n");
    }
    return 0;
}
