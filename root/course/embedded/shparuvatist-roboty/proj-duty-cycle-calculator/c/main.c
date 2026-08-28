#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PHASES 8

typedef struct {
    const char *name;      /* назва технологічної підфази */
    double current_ma;     /* струм споживання підфази, мА */
    double duration_ms;    /* тривалість підфази, мс */
} power_phase_t;

typedef struct {
    power_phase_t phases[MAX_PHASES];
    size_t phase_count;
    double sleep_current_ua;     /* струм сну всієї плати, мкА */
    double cycle_period_s;       /* повний період між циклами, с */
    double battery_capacity_mah; /* номінальна ємність батареї, мА·год */
    double derating_factor;      /* коефіцієнт корисної ємності (0.0..1.0) */
} power_profile_config_t;

typedef struct {
    double total_active_time_ms; /* сумарний час активного вікна t_on, мс */
    double total_active_charge_uc;/* сумарний активний заряд Q_on, мкКл (мкА·с) */
    double sleep_charge_uc;      /* заряд уві сні Q_off, мкКл */
    double avg_current_ua;       /* середній струм I_avg, мкА */
    double duty_cycle;           /* коефіцієнт шпаруватості D */
    double active_energy_share;  /* частка енергії активної фази, % */
    double sleep_energy_share;   /* частка енергії фази сну, % */
    double battery_lifetime_years;/* термін автономності, років */
    double saturation_period_s;  /* точка насичення T_90, с */
    bool valid;
} power_profile_report_t;

power_profile_report_t evaluate_power_profile(const power_profile_config_t *cfg) {
    power_profile_report_t rep = {0};
    if (!cfg || cfg->cycle_period_s <= 0.0 || cfg->phase_count == 0 || cfg->phase_count > MAX_PHASES) {
        return rep;
    }

    double t_on_ms = 0.0;
    double q_on_uc = 0.0;

    for (size_t i = 0; i < cfg->phase_count; ++i) {
        const power_phase_t *p = &cfg->phases[i];
        if (p->duration_ms < 0.0 || p->current_ma < 0.0) {
            return rep;
        }
        t_on_ms += p->duration_ms;
        /* заряд підфази в мкКл: мА * мс = мкКл (мкА * с) */
        q_on_uc += (p->current_ma * 1000.0) * (p->duration_ms / 1000.0);
    }

    double t_on_s = t_on_ms / 1000.0;
    if (t_on_s >= cfg->cycle_period_s) {
        return rep; /* активний час перевищує період циклу */
    }

    double t_off_s = cfg->cycle_period_s - t_on_s;
    double q_off_uc = cfg->sleep_current_ua * t_off_s;
    double q_total_uc = q_on_uc + q_off_uc;

    rep.total_active_time_ms = t_on_ms;
    rep.total_active_charge_uc = q_on_uc;
    rep.sleep_charge_uc = q_off_uc;
    rep.duty_cycle = t_on_s / cfg->cycle_period_s;
    rep.avg_current_ua = q_total_uc / cfg->cycle_period_s;
    rep.active_energy_share = (q_on_uc / q_total_uc) * 100.0;
    rep.sleep_energy_share = (q_off_uc / q_total_uc) * 100.0;

    if (rep.avg_current_ua > 0.0 && cfg->battery_capacity_mah > 0.0) {
        double eff_cap_uah = cfg->battery_capacity_mah * cfg->derating_factor * 1000.0;
        double hours = eff_cap_uah / rep.avg_current_ua;
        rep.battery_lifetime_years = hours / (24.0 * 365.25);
    }

    if (cfg->sleep_current_ua > 0.0) {
        /* T_90: період, за якого Q_off = 9 * Q_on */
        rep.saturation_period_s = (9.0 * q_on_uc) / cfg->sleep_current_ua;
    }

    rep.valid = true;
    return rep;
}

void print_profile_report(const power_profile_config_t *cfg, const power_profile_report_t *rep) {
    if (!rep || !rep->valid) {
        printf("Помилка: некоректні параметри профілю живлення!\n");
        return;
    }

    printf("================ ЗВІТ ЕНЕРГЕТИЧНОГО ПРОФІЛЮ ================\n");
    printf("Декомпозиція активного вікна (t_on = %.2f мс):\n", rep->total_active_time_ms);
    for (size_t i = 0; i < cfg->phase_count; ++i) {
        const power_phase_t *p = &cfg->phases[i];
        double q_phase = (p->current_ma * 1000.0) * (p->duration_ms / 1000.0);
        double share = (q_phase / rep->total_active_charge_uc) * 100.0;
        printf("  [%zu] %-20s | %6.2f мА | %6.2f мс | %7.1f мкКл (%5.1f%%)\n",
               i + 1, p->name, p->current_ma, p->duration_ms, q_phase, share);
    }
    printf("------------------------------------------------------------\n");
    printf("Шпаруватість D:             %.7f (%.5f%%)\n", rep->duty_cycle, rep->duty_cycle * 100.0);
    printf("Струм сну I_sleep:          %.2f мкА\n", cfg->sleep_current_ua);
    printf("Середній інтегральний струм: %.2f мкА\n", rep->avg_current_ua);
    printf("Розподіл енергії за цикл:   Активність: %.1f%% | Сон: %.1f%%\n",
           rep->active_energy_share, rep->sleep_energy_share);
    printf("Розрахункова автономність:  %.2f років\n", rep->battery_lifetime_years);
    printf("Точка насичення T_90:       %.0f с (%.1f хв)\n",
           rep->saturation_period_s, rep->saturation_period_s / 60.0);
    printf("============================================================\n");
}

int main(void) {
    power_profile_config_t lora_node = {
        .phases = {
            { .name = "Кварц + PLL старт",    .current_ma =  8.0, .duration_ms =  1.5 },
            { .name = "Живлення + АЦП давача",.current_ma =  5.0, .duration_ms =  3.0 },
            { .name = "Обробка + AES-128",    .current_ma = 18.0, .duration_ms =  1.2 },
            { .name = "Радіопередача LoRa TX",.current_ma = 45.0, .duration_ms = 22.0 },
            { .name = "Прийом квитанції RX",  .current_ma = 11.0, .duration_ms =  6.0 },
            { .name = "Перехід у глибокий сон",.current_ma=  3.0, .duration_ms =  0.3 }
        },
        .phase_count = 6,
        .sleep_current_ua = 2.8,       /* 2.8 мкА в глибокому сні */
        .cycle_period_s = 600.0,       /* 1 раз на 10 хвилин */
        .battery_capacity_mah = 2600.0,/* елемент Li-SOCl2 AA 2600 мА·год */
        .derating_factor = 0.85        /* 15% запас на саморозряд і температуру */
    };

    power_profile_report_t report = evaluate_power_profile(&lora_node);
    print_profile_report(&lora_node, &report);
    return 0;
}
