#ifndef DUTYCYCLE_H
#define DUTYCYCLE_H

/* Профіль споживання: інтегрування заряду за фазами робочого циклу.
 *
 * Модуль рахує те саме, що робить осцилограф із струмовим шунтом:
 * складає заряд усіх фаз, ділить на період і каже, хто саме з'їв заряд.
 */

#include "battery.h"

#define DC_MAX_PHASES 8

/* Одна активна фаза пробудження. Сон окремо: він триває стільки,
 * скільки лишилося від періоду. */
typedef struct {
    const char *name;
    double current_ma;
    double duration_ms;
} dc_phase;

typedef struct {
    const dc_phase *phases;      /* активні фази одного пробудження */
    size_t count;
    double sleep_current_ma;     /* струм глибокого сну разом з I_q стабілізатора */
    double period_s;             /* T_period — період повторення циклу */

    /* Депасиваційний імпульс: помірне навантаження раз на добу, щоб плівка
     * LiCl не встигала зростати. duration_ms = 0 — процедури немає. */
    dc_phase depassivation;
    double depassivation_period_s;
} duty_cycle_t;

/* Внесок однієї фази в заряд циклу. */
typedef struct {
    const char *name;
    double current_ma;
    double duration_ms;
    double charge_mas;      /* заряд фази за цикл, мА·с */
    double share;           /* частка від заряду циклу */
    double peukert_cost;    /* у скільки разів дорожче обійшовся цей заряд */
} dc_phase_result;

typedef struct {
    double active_s;             /* сумарна тривалість активних фаз */
    double rest_s;               /* скільки комірка відпочиває між пробудженнями */
    double q_active_mas;         /* Q_active — неподільний заряд одного пробудження */
    double q_sleep_mas;
    double q_depass_mas;
    double q_cycle_mas;          /* Q_cycle */
    double q_cycle_peukert_mas;  /* те саме з поправкою Пейкерта */
    double eta_pulse;            /* Q_cycle / Q_cycle_peukert — коефіцієнт імпульсності */
    double i_avg_ma;             /* I_avg = Q_cycle / T_period */
    double peak_current_ma;      /* найбільший струм у циклі */
    double peak_duration_ms;
    const char *peak_phase;

    size_t count;
    dc_phase_result per_phase[DC_MAX_PHASES];
    dc_phase_result sleep;
    dc_phase_result depass;
    int has_depass;
} duty_result_t;

est_status duty_cycle_compute(const battery_t *b,
                              const duty_cycle_t *dc,
                              duty_result_t *out);

#endif /* DUTYCYCLE_H */
