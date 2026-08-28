#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Режими інжективання гетеродина */
typedef enum {
    INJECTION_HIGH_SIDE = 0, /* f_LO > f_signal */
    INJECTION_LOW_SIDE  = 1  /* f_LO < f_signal */
} lo_injection_t;

/* Структура конфігурації подвійного перетворення */
typedef struct {
    double f_rf_hz;          /* Приймана радіочастота, Гц */
    double f_if1_hz;         /* Перша ПЧ, Гц */
    double f_if2_hz;         /* Друга ПЧ, Гц */
    lo_injection_t inj_lo1;  /* Режим першого гетеродина */
    lo_injection_t inj_lo2;  /* Режим другого гетеродина */
    double bw_roofing_hz;    /* Смуга руфінг-фільтра, Гц */
} double_conv_config_t;

/* Результати розрахунку частотного плану */
typedef struct {
    double f_lo1_hz;
    double f_img1_hz;
    double f_lo2_hz;
    double f_img2_hz;
    bool spectrum_inverted;
    int spur_count;
} double_conv_result_t;

/* Обчислення частотного плану */
double_conv_result_t calc_double_conversion(const double_conv_config_t *cfg) {
    double_conv_result_t res = {0};

    /* 1-ше перетворення */
    if (cfg->inj_lo1 == INJECTION_HIGH_SIDE) {
        res.f_lo1_hz  = cfg->f_rf_hz + cfg->f_if1_hz;
        res.f_img1_hz = cfg->f_rf_hz + 2.0 * cfg->f_if1_hz;
    } else {
        res.f_lo1_hz  = cfg->f_rf_hz - cfg->f_if1_hz;
        res.f_img1_hz = cfg->f_rf_hz - 2.0 * cfg->f_if1_hz;
    }

    /* 2-ге перетворення */
    if (cfg->inj_lo2 == INJECTION_HIGH_SIDE) {
        res.f_lo2_hz  = cfg->f_if1_hz + cfg->f_if2_hz;
        res.f_img2_hz = cfg->f_if1_hz + 2.0 * cfg->f_if2_hz;
    } else {
        res.f_lo2_hz  = cfg->f_if1_hz - cfg->f_if2_hz;
        res.f_img2_hz = cfg->f_if1_hz - 2.0 * cfg->f_if2_hz;
    }

    /* Підсумкова інверсія спектра: 2 інверсії скасовують одна одну */
    bool inv1 = (cfg->inj_lo1 == INJECTION_HIGH_SIDE);
    bool inv2 = (cfg->inj_lo2 == INJECTION_HIGH_SIDE);
    res.spectrum_inverted = (inv1 != inv2);

    return res;
}

/* Пошук комбінаційних завад (Spurs) до 5-го порядку */
void scan_spurs(const double_conv_config_t *cfg, double f_lo1_hz) {
    printf("\n--- Сканування комбінаційних завад (m*LO1 - n*RF -> IF1) ---\n");
    int found = 0;
    const double half_bw = cfg->bw_roofing_hz / 2.0;

    for (int m = 1; m <= 5; ++m) {
        for (int n = 1; n <= 5; ++n) {
            if (m == 1 && n == 1) continue; /* Фундаментальне перетворення */

            double mix_freq = fabs((double)m * f_lo1_hz - (double)n * cfg->f_rf_hz);
            double diff_from_if1 = fabs(mix_freq - cfg->f_if1_hz);

            if (diff_from_if1 <= half_bw) {
                printf("[УВАГА] Завада порядку K=%d (%d*LO1 - %d*RF): %.3f МГц (відхилення %.1f кГц)\n",
                       m + n, m, n, mix_freq / 1e6, diff_from_if1 / 1e3);
                found++;
            }
        }
    }
    if (found == 0) {
        printf("Комбінаційних завад нижчих порядків (K <= 10) у смузі руфінгу не виявлено.\n");
    }
}

int main(void) {
    double_conv_config_t cfg = {
        .f_rf_hz       = 14050000.0, /* 14.050 МГц */
        .f_if1_hz      = 45000000.0, /* 45.000 МГц */
        .f_if2_hz      =   455000.0, /* 455 кГц */
        .inj_lo1       = INJECTION_HIGH_SIDE,
        .inj_lo2       = INJECTION_HIGH_SIDE,
        .bw_roofing_hz =    15000.0  /* 15 кГц */
    };

    double_conv_result_t res = calc_double_conversion(&cfg);

    printf("====================================================\n");
    printf(" Калькулятор подвійного перетворення частоти\n");
    printf("====================================================\n");
    printf(" Вхідна частота RF  : %.3f МГц\n", cfg.f_rf_hz / 1e6);
    printf(" Перша ПЧ (IF1)     : %.3f МГц\n", cfg.f_if1_hz / 1e6);
    printf(" Друга ПЧ (IF2)     : %.3f МГц (%.0f кГц)\n", cfg.f_if2_hz / 1e6, cfg.f_if2_hz / 1e3);
    printf("----------------------------------------------------\n");
    printf(" Гетеродин 1 (LO1)  : %.3f МГц\n", res.f_lo1_hz / 1e6);
    printf(" Дзеркальний 1      : %.3f МГц (відстань %.3f МГц)\n", 
           res.f_img1_hz / 1e6, fabs(res.f_img1_hz - cfg.f_rf_hz) / 1e6);
    printf(" Гетеродин 2 (LO2)  : %.3f МГц\n", res.f_lo2_hz / 1e6);
    printf(" Дзеркальний 2      : %.3f МГц (відстань від IF1: %.1f кГц)\n", 
           res.f_img2_hz / 1e6, fabs(res.f_img2_hz - cfg.f_if1_hz) / 1e3);
    printf(" Орієнтація спектра : %s\n", 
           res.spectrum_inverted ? "ІНВЕРТОВАНИЙ (LSB)" : "ПРЯМИЙ (USB)");
    printf("====================================================\n");

    scan_spurs(&cfg, res.f_lo1_hz);

    return 0;
}
