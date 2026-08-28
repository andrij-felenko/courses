#include <stdio.h>
#include <stdbool.h>

typedef struct {
    double active_current_ma;    /* струм в активному стані, мА */
    double active_time_ms;       /* тривалість активного спалаху, мс */
    double sleep_current_ua;     /* струм сну, мкА */
    double period_s;             /* період повторення циклу, с */
    double battery_capacity_mah; /* номінальна ємність батареї, мА·год */
    double battery_derating;     /* коефіцієнт корисної віддачі ємності (0.0..1.0) */
} duty_config_t;

typedef struct {
    double duty_cycle;           /* коефіцієнт заповнення D */
    double avg_current_ua;       /* середній інтегральний струм, мкА */
    double active_energy_pct;    /* частка заряду активної фази, % */
    double sleep_energy_pct;     /* частка заряду фази сну, % */
    double lifetime_years;       /* розрахунковий термін служби, років */
    double saturation_period_s;  /* період практичного насичення T_90, с */
    bool valid;
} duty_result_t;

duty_result_t calculate_duty_profile(const duty_config_t *cfg) {
    duty_result_t res = {0};
    if (!cfg || cfg->period_s <= 0.0 || cfg->active_time_ms <= 0.0) {
        return res;
    }

    double t_on_s = cfg->active_time_ms / 1000.0;
    if (t_on_s > cfg->period_s) {
        return res;
    }
    double t_off_s = cfg->period_s - t_on_s;

    /* Заряди фаз у мкА·с (мікрокулонах) */
    double i_on_ua = cfg->active_current_ma * 1000.0;
    double q_on = i_on_ua * t_on_s;
    double q_off = cfg->sleep_current_ua * t_off_s;
    double q_total = q_on + q_off;

    res.duty_cycle = t_on_s / cfg->period_s;
    res.avg_current_ua = q_total / cfg->period_s;
    res.active_energy_pct = (q_on / q_total) * 100.0;
    res.sleep_energy_pct = (q_off / q_total) * 100.0;

    double eff_cap_uah = cfg->battery_capacity_mah * cfg->battery_derating * 1000.0;
    double lifetime_hours = eff_cap_uah / res.avg_current_ua;
    res.lifetime_years = lifetime_hours / (24.0 * 365.25);

    /* Точка насичення T_90: Q_off = 9 * Q_on */
    if (cfg->sleep_current_ua > 0.0) {
        res.saturation_period_s = 9.0 * (i_on_ua / cfg->sleep_current_ua) * t_on_s;
    }

    res.valid = true;
    return res;
}

int main(void) {
    duty_config_t config = {
        .active_current_ma = 45.0,     /* 45 мА (передавач + ядро) */
        .active_time_ms = 15.0,        /* 15 мс активного вікна */
        .sleep_current_ua = 3.2,       /* 3.2 мкА струм спокою */
        .period_s = 300.0,             /* 1 передача раз на 5 хвилин */
        .battery_capacity_mah = 2400.0,/* елемент AA 2400 мА·год */
        .battery_derating = 0.85       /* 15% запас на саморозряд і мороз */
    };

    duty_result_t r = calculate_duty_profile(&config);
    if (r.valid) {
        printf("Шпаруватість D:        %.6f (%.4f%%)\n", r.duty_cycle, r.duty_cycle * 100.0);
        printf("Середній струм:        %.2f мкА\n", r.avg_current_ua);
        printf("Розподіл енергії:      Активна = %.1f%%, Сон = %.1f%%\n",
               r.active_energy_pct, r.sleep_energy_pct);
        printf("Термін автономності:   %.2f років\n", r.lifetime_years);
        printf("Точка насичення T_90:  %.0f с (%.1f хв)\n",
               r.saturation_period_s, r.saturation_period_s / 60.0);
    }
    return 0;
}
