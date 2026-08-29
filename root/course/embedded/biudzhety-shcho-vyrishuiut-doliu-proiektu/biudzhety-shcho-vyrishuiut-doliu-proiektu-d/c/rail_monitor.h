#ifndef RAIL_MONITOR_H
#define RAIL_MONITOR_H

/*
 * Нагляд за шиною живлення.
 *
 * Середній струм ще нічого не гарантує: старт радіопередавача рве з шини
 * сотні міліампер за одиниці мікросекунд, і якщо напруга бодай на десятки
 * наносекунд провалиться нижче порогу BOR, процесор перезавантажиться.
 * Монітор тримає мінімум за весь час роботи й рахує події просідання.
 */

#include "budget_types.h"

typedef struct {
    uint16_t nominal_mv;  /* номінал шини */
    uint16_t warn_mv;     /* поріг тривоги: запас до BOR вичерпується */
    uint16_t bor_mv;      /* поріг схеми скидання за зниження напруги */
} rail_limits_t;

typedef struct {
    rail_limits_t limits;
    uint16_t      last_mv;
    uint16_t      min_mv;
    uint32_t      samples;
    uint32_t      sag_events;
    uint32_t      brownout_events;
} rail_monitor_t;

bool rail_monitor_init(rail_monitor_t *rail, const rail_limits_t *limits);

/* Приймає черговий відлік АЦП у мілівольтах і повертає прапорці порушень. */
budget_flags_t rail_monitor_sample(rail_monitor_t *rail, uint16_t millivolts);

/* Запас від найгіршого зафіксованого відліку до порогу BOR, мВ. */
int32_t rail_monitor_headroom_mv(const rail_monitor_t *rail);

/*
 * Розрахункове просідання шини на імпульсі струму:
 *   dV = I_peak * ESR + I_peak * dt / C_bulk
 * Дозволяє перевірити ємнісний буфер ще до першого вмикання передавача.
 */
uint32_t rail_estimate_droop_mv(uint32_t peak_ma, uint32_t esr_mohm,
                                uint32_t bulk_uf, uint32_t burst_us);

#endif /* RAIL_MONITOR_H */
