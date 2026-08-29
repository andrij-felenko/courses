#ifndef THERMAL_BUDGET_H
#define THERMAL_BUDGET_H

/*
 * Тепловий бюджет кристала: T_j = T_a + P * R_th_JA.
 *
 * Температури зберігаються в десятих частках градуса (°C * 10) — цілочислова
 * арифметика тримає роздільність 0.1 °C без плаваючої коми, якої в дешевому
 * ядрі просто немає. Тепловий опір зберігається в м°C/Вт (R_th * 1000).
 */

#include "budget_types.h"

typedef struct {
    int16_t  tj_max_dc;      /* максимальна температура переходу, °C * 10 */
    int16_t  warn_margin_dc; /* за скільки до межі піднімати тривогу */
    int16_t  hysteresis_dc;  /* наскільки треба охолонути, щоб зняти тривогу */
    uint32_t rth_ja_mcw;     /* тепловий опір кристал-середовище, м°C/Вт */
} thermal_limits_t;

typedef struct {
    thermal_limits_t limits;
    int16_t          ambient_dc;  /* температура всередині корпусу */
    int16_t          junction_dc; /* поточна оцінка температури кристала */
    int16_t          peak_dc;     /* найгірше значення за весь час роботи */
    uint32_t         power_mw;    /* поточні теплові втрати вузла */
    bool             throttled;   /* чи ввімкнено зниження навантаження */
    uint32_t         trip_events;
} thermal_monitor_t;

bool thermal_monitor_init(thermal_monitor_t *tm, const thermal_limits_t *limits);

/* Оцінка температури кристала за середовищем і втратами. */
int16_t thermal_junction_dc(int16_t ambient_dc, uint32_t power_mw,
                            uint32_t rth_ja_mcw);

/* Максимальна потужність, яку вузол може розсіяти при заданому середовищі. */
uint32_t thermal_max_power_mw(const thermal_limits_t *limits, int16_t ambient_dc);

/* Струм, який ще витримає лінійний стабілізатор при перепаді (U_in - U_out). */
uint32_t thermal_ldo_max_current_ma(const thermal_limits_t *limits,
                                    int16_t ambient_dc, uint32_t dropout_mv);

budget_flags_t thermal_monitor_sample(thermal_monitor_t *tm, int16_t ambient_dc,
                                      uint32_t power_mw);

#endif /* THERMAL_BUDGET_H */
