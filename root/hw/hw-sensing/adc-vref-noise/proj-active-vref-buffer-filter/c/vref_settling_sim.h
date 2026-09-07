#ifndef VREF_SETTLING_SIM_H
#define VREF_SETTLING_SIM_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @brief Параметри буферного операційного підсилювача та фільтра VREF
 */
typedef struct {
    double vref_nominal_v;    /* Номінальна вихідна опорна напруга, В */
    double gbw_hz;            /* Добуток коефіцієнта підсилення на смугу (GBW), Гц */
    double r_out_open_loop;   /* Розімкнений вихідний опір ОП, Ом */
    double c_filt_f;          /* Ємність зовнішнього вихідного конденсатора фільтра, Ф */
    double esr_c_filt_ohm;    /* Еквівалентний послідовний опір (ESR) конденсатора, Ом */
    double r_iso_ohm;         /* Опір ізолюючого резистора компенсації петлі, Ом */
    double c_feedback_f;      /* Ємність конденсатора зворотного зв'язку (in-loop), Ф */
} vref_buffer_config_t;

/**
 * @brief Параметри комутаційного імпульсу матриці CDAC SAR АЦП
 */
typedef struct {
    unsigned int resolution_bits; /* Розрядність АЦП (наприклад, 16 або 24 біти) */
    double c_sample_f;            /* Сумарна ємність вибірки матриці CDAC, Ф */
    double v_step_v;              /* Стрибок напруги перемикання матриці (найгірший випадок MSB), В */
    double t_settle_budget_s;     /* Часовий бюджет на встановлення напруги такту, с */
} cdac_switch_event_t;

/**
 * @brief Результати числового моделювання динамічного відгуку VREF
 */
typedef struct {
    double max_voltage_drop_v;    /* Максимальне динамічне просідання напруги, В */
    double residual_error_v;      /* Залишкова похибка напруги в кінці такту вибірки, В */
    double error_lsb;             /* Похибка встановлення у частках LSB */
    double phase_margin_deg;      /* Оцінка фазового запасу петлі зворотного зв'язку, градуси */
    bool is_settled_within_half_lsb; /* Прапорець успішного встановлення точніше 0.5 LSB */
} vref_sim_result_t;

/**
 * @brief Виконує покрокове числове моделювання динамічного встановлення VREF
 *
 * @param buf Параметри буфера та накопичувального конденсатора
 * @param cdac Параметри комутованої матриці ємностей АЦП
 * @param dt_s Крок інтегрування дискретної моделі, с
 * @param result Покажчик на структуру для запису результатів
 * @return true у разі успішного розрахунку, false при помилці валідації параметрів
 */
bool vref_simulate_cdac_settling(
    const vref_buffer_config_t *buf,
    const cdac_switch_event_t *cdac,
    double dt_s,
    vref_sim_result_t *result
);

/**
 * @brief Обчислює аналітичну оцінку фазового запасу буфера з in-loop компенсацією
 *
 * @param buf Параметри конфігурації активного буфера
 * @return Фазовий запас у градусах
 */
double vref_calculate_phase_margin(const vref_buffer_config_t *buf);

#endif /* VREF_SETTLING_SIM_H */
