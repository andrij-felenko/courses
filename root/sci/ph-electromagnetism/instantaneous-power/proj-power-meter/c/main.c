#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>

/* Структура результатів вимірювання електроенергії */
typedef struct {
    double active_power;      /* P, Активна потужність (Вт) */
    double reactive_power;    /* Q, Реактивна потужність (вар) */
    double apparent_power;    /* S, Повна потужність (В·А) */
    double v_rms;             /* Vrms, Діюча напруга (В) */
    double i_rms;             /* Irms, Діючий струм (А) */
    double power_factor;      /* PF, Коефіцієнт потужності (cos φ) */
    double p_max;             /* Пікова миттєва потужність (Вт) */
    double p_min;             /* Мінімальна миттєва потужність (Вт) */
} power_metrics_t;

/**
 * Обчислення метрик потужності за буферами дискретних відліків.
 *
 * @param vbuf      Масив відліків напруги (В)
 * @param ibuf      Масив відліків струму (А)
 * @param count     Кількість відліків у буфері
 * @param result    Структура для запису обчислених результатів
 * @return true у разі успішного розрахунку, false при помилці аргументів
 */
bool compute_power_metrics(const double *vbuf, const double *ibuf, size_t count, power_metrics_t *result) {
    if (!vbuf || !ibuf || !result || count == 0) {
        return false;
    }

    double sum_p = 0.0;
    double sum_v2 = 0.0;
    double sum_i2 = 0.0;
    double p_max = -1e9;
    double p_min = 1e9;

    /* Поточкове накопичення суматорів у часовій області */
    for (size_t n = 0; n < count; ++n) {
        double v = vbuf[n];
        double i = ibuf[n];
        double p_inst = v * i;

        sum_p += p_inst;
        sum_v2 += v * v;
        sum_i2 += i * i;

        if (p_inst > p_max) p_max = p_inst;
        if (p_inst < p_min) p_min = p_inst;
    }

    double inv_count = 1.0 / (double)count;
    double active_p = sum_p * inv_count;
    double v_rms = sqrt(sum_v2 * inv_count);
    double i_rms = sqrt(sum_i2 * inv_count);
    double apparent_s = v_rms * i_rms;

    /* Обчислення Q із захистом від від'ємного підкореневого виразу через округлення */
    double reactive_q = 0.0;
    double s2_minus_p2 = (apparent_s * apparent_s) - (active_p * active_p);
    if (s2_minus_p2 > 0.0) {
        reactive_q = sqrt(s2_minus_p2);
    }

    /* Захист від ділення на нуль та обмеження діапазону PF [-1.0, 1.0] */
    double pf = 1.0;
    if (apparent_s > 1e-6) {
        pf = active_p / apparent_s;
        if (pf > 1.0) pf = 1.0;
        if (pf < -1.0) pf = -1.0;
    }

    result->active_power   = active_p;
    result->reactive_power = reactive_q;
    result->apparent_power = apparent_s;
    result->v_rms          = v_rms;
    result->i_rms          = i_rms;
    result->power_factor   = pf;
    result->p_max          = p_max;
    result->p_min          = p_min;

    return true;
}
