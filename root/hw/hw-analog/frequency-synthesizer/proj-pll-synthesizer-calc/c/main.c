#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура вхідних параметрів ФАПЧ */
typedef struct {
    double f_out_hz;       /* Вихідна частота (Гц) */
    double f_pfd_hz;       /* Опорна частота на PFD (Гц) */
    double i_cp_a;         /* Струм помпи заряду (А) */
    double k_vco_hz_v;     /* Крутизна VCO (Гц/В) */
    double target_fc_hz;   /* Бажана смуга петлі (Гц) */
    double target_pm_deg;  /* Бажаний запас по фазі (градуси) */
    double fom_db;         /* Показник якості PFD (дБн/Гц, наприклад -230) */
    double vco_noise_1mhz; /* Власний шум VCO на відбудові 1 МГц (дБн/Гц) */
} pll_params_t;

/* Структура результатів розрахунку */
typedef struct {
    double n_div;          /* Коефіцієнт ділення N */
    double c1_farad;       /* Ємність C1 (Ф) */
    double r1_ohm;         /* Опір R1 (Ом) */
    double c2_farad;       /* Ємність C2 (Ф) */
    double omega_n;        /* Власна частота петлі (рад/с) */
    double zeta;           /* Коефіцієнт демпфування */
    double actual_pm_deg;  /* Фактичний запас по фазі (градуси) */
    double t_lock_us;      /* Час захоплення до 1 кГц (мкс) */
    double inband_noise;   /* Внутрішньосмуговий шум (дБн/Гц) */
    double total_noise_100k;/* Сумарний шум на відбудові 100 кГц (дБн/Гц) */
} pll_result_t;

/* Функція розрахунку параметрів петлі ФАПЧ */
int pll_calculate(const pll_params_t *p, pll_result_t *res) {
    if (!p || !res || p->f_pfd_hz <= 0.0 || p->f_out_hz <= 0.0) {
        return -1;
    }

    /* 1. Коефіцієнт ділення N */
    res->n_div = p->f_out_hz / p->f_pfd_hz;

    double wc = 2.0 * M_PI * p->target_fc_hz;
    double k_vco_rad = 2.0 * M_PI * p->k_vco_hz_v;
    double pm_rad = p->target_pm_deg * (M_PI / 180.0);

    /* 2. Розрахунок C1 */
    res->c1_farad = (p->i_cp_a * k_vco_rad * cos(pm_rad)) /
                    (2.0 * M_PI * res->n_div * wc * wc);

    /* 3. Розрахунок R1 (для zeta ~ 0.7) */
    res->zeta = 0.707;
    res->r1_ohm = (2.0 * res->zeta) / (wc * res->c1_farad);

    /* 4. Розрахунок C2 (C1 / 10 для забезпечення PM) */
    res->c2_farad = res->c1_farad / 10.0;

    /* 5. Резонансна частота петлі omega_n */
    res->omega_n = sqrt((p->i_cp_a * k_vco_rad) /
                        (2.0 * M_PI * res->n_div * res->c1_farad));

    /* 6. Перевірка фактичного запасу по фазі */
    double c_eq = (res->c1_farad * res->c2_farad) / (res->c1_farad + res->c2_farad);
    double phi_1 = atan(wc * res->r1_ohm * res->c1_farad);
    double phi_2 = atan(wc * res->r1_ohm * c_eq);
    res->actual_pm_deg = (phi_1 - phi_2) * (180.0 / M_PI);

    /* 7. Час встановлення частоти при стрибку на 50 МГц до точності 1 кГц */
    double f_step = 50.0e6;
    double f_tol = 1000.0;
    res->t_lock_us = (-log(f_tol / f_step) / (res->zeta * res->omega_n)) * 1.0e6;

    /* 8. Розрахунок фазового шуму */
    res->inband_noise = p->fom_db + 10.0 * log10(p->f_pfd_hz) + 20.0 * log10(res->n_div);

    /* Оцінка шуму VCO на відбудові 100 кГц (падіння -20 дБ/дек від 1 МГц) */
    double vco_100k = p->vco_noise_1mhz + 20.0 * log10(1.0e6 / 100.0e3);

    /* Сума потужностей внутрішньосмугового та VCO шуму */
    double p_inband = pow(10.0, res->inband_noise / 10.0);
    double p_vco = pow(10.0, vco_100k / 10.0);
    res->total_noise_100k = 10.0 * log10(p_inband + p_vco);

    return 0;
}

int main(void) {
    pll_params_t params = {
        .f_out_hz = 2400.0e6,
        .f_pfd_hz = 25.0e6,
        .i_cp_a = 0.0025,
        .k_vco_hz_v = 30.0e6,
        .target_fc_hz = 100.0e3,
        .target_pm_deg = 50.0,
        .fom_db = -230.0,
        .vco_noise_1mhz = -120.0
    };

    pll_result_t res;
    if (pll_calculate(&params, &res) == 0) {
        printf("=== Результати розрахунку ФАПЧ 2.4 ГГц (C) ===\n");
        printf("Коефіцієнт N: %.1f\n", res.n_div);
        printf("Петльовий фільтр: C1 = %.3f нФ, R1 = %.1f Ом, C2 = %.1f пФ\n",
               res.c1_farad * 1e9, res.r1_ohm, res.c2_farad * 1e12);
        printf("Частота петлі (omega_n): %.1f крад/с\n", res.omega_n / 1000.0);
        printf("Запас по фазі (PM): %.1f deg\n", res.actual_pm_deg);
        printf("Час захоплення (t_lock): %.2f мкс\n", res.t_lock_us);
        printf("Внутрішньосмуговий шум: %.1f дБн/Гц\n", res.inband_noise);
        printf("Шум на відбудові 100 кГц: %.1f дБн/Гц\n", res.total_noise_100k);
    }
    return 0;
}
