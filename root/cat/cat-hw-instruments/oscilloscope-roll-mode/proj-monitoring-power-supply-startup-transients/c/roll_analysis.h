#ifndef ROLL_ANALYSIS_H
#define ROLL_ANALYSIS_H

#include <stddef.h>
#include <stdbool.h>

/* Відлік оцифрованого сигналу в режимі Roll Mode */
typedef struct {
    double timestamp_sec; /* Часова мітка вибірки в секундах від початку запису */
    double voltage_v;     /* Амплітудне значення напруги у вольтах */
} roll_sample_t;

/* Курсорні відліки для аналізу сигналу */
typedef struct {
    roll_sample_t t1; /* Перша курсорна позначка */
    roll_sample_t t2; /* Друга курсорна позначка */
} roll_cursors_t;

/* Результат аналізу пускового перехідного процесу */
typedef struct {
    bool is_valid;             /* Прапор успішності обчислення */
    double transient_time_sec; /* Тривалість пускового процесу Δt у секундах */
    double steady_voltage_v;   /* Усталене значення напруги */
} transient_result_t;

/* Результат прогнозування часу розряду акумулятора */
typedef struct {
    bool is_valid;               /* Прапор успішності прогнозування */
    double discharge_rate_v_per_s;/* Швидкість падіння напруги dV/dt (В/с) */
    double remaining_time_sec;   /* Прогнозований залишковий час до відсічки у секундах */
} discharge_result_t;

/**
 * Обчислення тривалості пускового перехідного процесу.
 * Функція шукає момент часу, після якого сигнал більше не виходить за межі 
 * допускної зони (tolerance_pct) від усталеної напруги steady_voltage_v.
 */
transient_result_t calculate_transient_duration(
    const roll_sample_t *samples,
    size_t sample_count,
    double steady_voltage_v,
    double tolerance_pct
);

/**
 * Прогнозування часу розряду акумулятора за двома курсорними позначками.
 * Розраховує лінійну екстраполяцію dV/dt між курсорами t1 та t2 
 * і обчислює час досягнення порогової напруги cutoff_voltage_v.
 */
discharge_result_t estimate_battery_discharge_time(
    const roll_cursors_t *cursors,
    double cutoff_voltage_v
);

#endif /* ROLL_ANALYSIS_H */
