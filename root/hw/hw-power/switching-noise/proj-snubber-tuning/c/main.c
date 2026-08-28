#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double f1_mhz;        /* Початкова частота дзвіну (МГц) */
    double f2_mhz;        /* Частота з доданою ємністю (МГц) */
    double c_add_pf;      /* Додана калібрувальна ємність (пФ) */
    double vin_volts;     /* Вхідна напруга перетворювача (В) */
    double fsw_khz;       /* Частота комутації (кГц) */
    double kc_factor;     /* Коефіцієнт кратності ємності снубера (типово 2.0-3.0) */
    double l_post_uh;     /* Індуктивність вторинного дроселя (мкГн, 0 якщо нема) */
    double c_post_uf;     /* Ємність вторинного конденсатора (мкФ) */
} SnubberInput;

typedef struct {
    double c_par_pf;      /* Розрахована паразитна ємність (пФ) */
    double l_par_nh;      /* Розрахована паразитна індуктивність (нГн) */
    double z0_ohms;       /* Характеристичний імпеданс (Ом) */
    double c_snub_pf;     /* Рекомендована ємність снубера (пФ) */
    double r_snub_ohms;   /* Рекомендований опір снубера (Ом) */
    double p_snub_mw;     /* Теплова потужність розсіювання на резисторі (мВт) */
    double fc_post_khz;   /* Частота зрізу вторинного фільтра (кГц) */
    double att_100mhz_db; /* Придушення вторинного фільтра на 100 МГц (дБ) */
    bool is_valid;        /* Прапорець коректності вхідних даних */
} SnubberResult;

SnubberResult calculate_snubber(const SnubberInput *in) {
    SnubberResult res;
    res.is_valid = false;

    if (!in || in->f1_mhz <= 0.0 || in->f2_mhz <= 0.0 || in->c_add_pf <= 0.0) {
        return res;
    }
    if (in->f2_mhz >= in->f1_mhz) {
        /* Додана ємність зобов'язана знижувати резонансну частоту */
        return res;
    }

    double ratio = in->f1_mhz / in->f2_mhz;
    double ratio_sq = ratio * ratio;

    /* C_par = C_add / ((f1 / f2)^2 - 1) */
    res.c_par_pf = in->c_add_pf / (ratio_sq - 1.0);

    /* L_par = 1 / (4 * pi^2 * f1^2 * C_par) */
    double f1_hz = in->f1_mhz * 1.0e6;
    double c_par_farads = res.c_par_pf * 1.0e-12;
    double l_par_henry = 1.0 / (4.0 * M_PI * M_PI * f1_hz * f1_hz * c_par_farads);
    res.l_par_nh = l_par_henry * 1.0e9;

    /* Z_0 = sqrt(L_par / C_par) */
    res.z0_ohms = sqrt(l_par_henry / c_par_farads);

    /* Параметри демпфера */
    double kc = (in->kc_factor >= 1.0) ? in->kc_factor : 3.0;
    res.c_snub_pf = kc * res.c_par_pf;

    double c_total_snub_farads = (res.c_par_pf + res.c_snub_pf) * 1.0e-12;
    res.r_snub_ohms = sqrt(l_par_henry / c_total_snub_farads);

    /* Втрати потужності: P = C_snub * Vin^2 * f_sw */
    double fsw_hz = in->fsw_khz * 1.0e3;
    double c_snub_farads = res.c_snub_pf * 1.0e-12;
    double p_watts = c_snub_farads * (in->vin_volts * in->vin_volts) * fsw_hz;
    res.p_snub_mw = p_watts * 1.0e3;

    /* Вторинний LC-фільтр */
    if (in->l_post_uh > 0.0 && in->c_post_uf > 0.0) {
        double l_post_h = in->l_post_uh * 1.0e-6;
        double c_post_f = in->c_post_uf * 1.0e-6;
        double fc_hz = 1.0 / (2.0 * M_PI * sqrt(l_post_h * c_post_f));
        res.fc_post_khz = fc_hz * 1.0e-3;

        double f_target_hz = 100.0e6;
        if (f_target_hz > fc_hz) {
            res.att_100mhz_db = 40.0 * log10(f_target_hz / fc_hz);
        } else {
            res.att_100mhz_db = 0.0;
        }
    } else {
        res.fc_post_khz = 0.0;
        res.att_100mhz_db = 0.0;
    }

    res.is_valid = true;
    return res;
}

int main(void) {
    SnubberInput input = {
        .f1_mhz = 180.0,
        .f2_mhz = 95.0,
        .c_add_pf = 470.0,
        .vin_volts = 24.0,
        .fsw_khz = 500.0,
        .kc_factor = 3.0,
        .l_post_uh = 0.47,
        .c_post_uf = 10.0
    };

    SnubberResult res = calculate_snubber(&input);
    if (!res.is_valid) {
        fprintf(stderr, "Помилка: некоректні вхідні дані вимірювань.\n");
        return 1;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ДЕМПФЕРА ===\n");
    printf("Паразитна ємність вузла C_par:       %.1f пФ\n", res.c_par_pf);
    printf("Паразитна індуктивність L_par:       %.2f нГн\n", res.l_par_nh);
    printf("Хвильовий опір контуру Z_0:          %.2f Ом\n\n", res.z0_ohms);

    printf("Рекомендована ємність снубера C_sn:  %.1f пФ (оберіть C0G/NP0)\n", res.c_snub_pf);
    printf("Рекомендований опір снубера R_sn:    %.2f Ом (безіндуктивний SMD)\n", res.r_snub_ohms);
    printf("Потужність розсіювання на R_sn:      %.1f мВт (типорозмір 0805/1206)\n\n", res.p_snub_mw);

    if (res.fc_post_khz > 0.0) {
        printf("=== ВТОРИННИЙ LC-ФІЛЬТР ===\n");
        printf("Частота зрізу f_c:                   %.1f кГц\n", res.fc_post_khz);
        printf("Розрахункове придушення на 100 МГц:  %.1f дБ\n", res.att_100mhz_db);
    }

    return 0;
}
