#ifndef FM_TIME_H
#define FM_TIME_H

#include <stdbool.h>
#include <stdint.h>

/* Бортовий час — вільний лічильник мілісекунд, що переповнюється кожні ~49.7 доби.
   Різниця беззнакових цілих переповнення переживає коректно, а ось порівняння
   `now > stamp + ms` — ні: саме на такому порівнянні автомат після сорока дев'яти
   діб напрацювання перестав би бачити свої тайм-аути. */

static inline uint32_t fm_age_ms(uint32_t now_ms, uint32_t stamp_ms)
{
    return (uint32_t)(now_ms - stamp_ms);
}

static inline bool fm_elapsed(uint32_t now_ms, uint32_t stamp_ms, uint32_t span_ms)
{
    return fm_age_ms(now_ms, stamp_ms) >= span_ms;
}

#endif /* FM_TIME_H */
