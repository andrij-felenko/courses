/* Розрахунок робочої точки автономного вузла: профіль споживання,
 * обернена задача під цільовий термін служби, крива насичення
 * й перевірка годинного ліміту часу в ефірі. */
#include "duty_cycle.h"

#include <math.h>
#include <stdio.h>

static void print_seconds(const char *label, double seconds)
{
    if (isinf(seconds)) {
        printf("%s без витоків не настає ніколи\n", label);
        return;
    }
    if (seconds >= 3600.0)
        printf("%s%.0f с (%.1f год)\n", label, seconds, seconds / 3600.0);
    else
        printf("%s%.0f с (%.1f хв)\n", label, seconds, seconds / 60.0);
}

static void print_profile(const duty_config *cfg, const duty_result *r)
{
    printf("Робоча точка: T = %.0f с, t_on = %.0f мс, I_on = %.0f мкА, I_sleep = %.1f мкА\n",
           cfg->period_s, cfg->t_on_s * 1000.0, cfg->i_on_ua, cfg->i_sleep_ua);
    printf("  шпаруватість D    : %.7f (%.5f %%)\n", r->duty, r->duty * 100.0);
    printf("  середній струм    : %.2f мкА\n", r->i_avg_ua);
    printf("  заряд за цикл     : активний %.0f мкА·с, сон %.0f мкА·с (k = %.2f)\n",
           r->q_on_uas, r->q_off_uas, r->k_energy);
    printf("  розподіл заряду   : спалах %.1f %%, сон %.1f %%\n",
           r->active_share_pct, r->sleep_share_pct);
    printf("  автономність      : %.0f год (%.1f років)\n",
           r->lifetime_h, r->lifetime_years);
    print_seconds("  рівновага k = 1   : ", r->t_eq_s);
    print_seconds("  насичення T_90    : ", r->t_sat_s);
}

static void print_airtime(const etsi_band *band, double toa_s, double period_s)
{
    airtime_check air;
    duty_status st = duty_check_airtime(band, toa_s, period_s, &air);

    if (st != DUTY_OK) {
        fprintf(stderr, "Бюджет ефіру не порахувати: %s\n", duty_strerror(st));
        return;
    }

    printf("\nETSI %s (%.2f–%.2f МГц, D <= %.1f %%, до %+.0f дБм); "
           "пакет %.2f с, період %.0f с\n",
           band->name, band->f_lo_mhz, band->f_hi_mhz,
           band->duty_limit * 100.0, band->max_erp_dbm, toa_s, period_s);
    printf("  дозволено за годину : %.1f с\n", air.allowance_s);
    printf("  фактично за годину  : %.1f с (%.0f %% ліміту)\n",
           air.used_s, air.used_pct);
    printf("  один пакет з'їдає   : %.2f %% бюджету, за годину влізе %d штук\n",
           air.packet_share_pct, (int)floor(air.packets_per_hour));
    printf("  мінімальний період  : %.0f с — %s\n", air.min_period_s,
           air.compliant ? "ліміт дотримано" : "стек заблокує вихід в ефір");
}

int main(void)
{
    /* Вузол LoRaWAN зі статті: елемент Li-SOCl2 типорозміру AA,
     * спалах 30 мс при 40 мА, виміряний струм спокою плати 2.8 мкА. */
    duty_config node;
    duty_result r;
    duty_status st;
    double t_min_s;
    size_t i;

    static const double scan_s[] = { 10.0, 60.0, 300.0, 1800.0, 3600.0, 21600.0, 86400.0 };

    node.i_on_ua = 40000.0;
    node.t_on_s = 0.030;
    node.i_sleep_ua = 2.8;
    node.period_s = 600.0;
    node.capacity_mah = 2600.0;
    node.derating = 0.85;

    st = duty_evaluate(&node, &r);
    if (st != DUTY_OK) {
        fprintf(stderr, "Профіль неспроможний: %s\n", duty_strerror(st));
        return 1;
    }
    print_profile(&node, &r);

    /* Обернена задача: під який період вузол дотягує рівно до 5 років. */
    st = duty_min_period(&node, 5.0, &t_min_s);
    if (st == DUTY_OK)
        printf("\nМінімальний період для 5 років: %.1f с (%.1f хв)\n",
               t_min_s, t_min_s / 60.0);
    else
        printf("\n5 років недосяжні: %s\n", duty_strerror(st));

    /* Та сама вимога, але плата з паразитним витоком: період уже не рятує. */
    {
        duty_config leaky = node;
        leaky.i_sleep_ua = 60.0;
        st = duty_min_period(&leaky, 5.0, &t_min_s);
        if (st == DUTY_OK)
            printf("Плата з витоком 60 мкА: період %.0f с\n", t_min_s);
        else
            printf("Плата з витоком 60 мкА: %s\n", duty_strerror(st));
    }

    /* Скан періодів: видно, як крива лягає на плато I_sleep. */
    printf("\n     T, с           D   I_avg, мкА     роки   сон, %%\n");
    for (i = 0; i < sizeof scan_s / sizeof scan_s[0]; ++i) {
        duty_config probe = node;
        duty_result pr;

        probe.period_s = scan_s[i];
        st = duty_evaluate(&probe, &pr);
        if (st != DUTY_OK) {
            fprintf(stderr, "T = %.0f с: %s\n", scan_s[i], duty_strerror(st));
            continue;
        }
        printf("%9.0f  %10.7f   %10.2f  %7.1f  %7.1f%s\n",
               scan_s[i], pr.duty, pr.i_avg_ua, pr.lifetime_years,
               pr.sleep_share_pct,
               scan_s[i] >= r.t_sat_s ? "   <- за точкою насичення" : "");
    }

    /* Регулятор: довгий пакет SF12 тривалістю 1.48 с у смузі g1. */
    {
        const etsi_band *g1 = etsi_band_for(868.1);
        const double toa_sf12_s = 1.48;

        if (g1 == NULL) {
            fprintf(stderr, "Частота 868.1 МГц поза сіткою EU868\n");
            return 1;
        }
        print_airtime(g1, toa_sf12_s, node.period_s);
        print_airtime(g1, toa_sf12_s, 60.0); /* щохвилини — ліміт злітає */
    }

    return 0;
}
