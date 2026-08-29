#ifndef TIMEBASE_H
#define TIMEBASE_H

#include <stdint.h>

// Монотонний час пристрою з плавним підтягуванням до еталона сервера.
// Хід прискорюють або сповільнюють щонайбільше на SLEW_PERCENT, тому
// повернена мітка часу НІКОЛИ не йде назад — навіть коли сервер каже,
// що годинник поспішає на три секунди.
#define TIMEBASE_SLEW_PERCENT 5

typedef struct {
    int32_t  offset_ms;    // чинна поправка до сирого лічильника
    int32_t  pending_ms;   // скільки поправки ще не внесено
    uint32_t last_raw_ms;
} timebase_t;

void timebase_init(timebase_t *tb, uint32_t raw_now);
uint32_t timebase_now(const timebase_t *tb, uint32_t raw_now);
void timebase_set_reference(timebase_t *tb, uint32_t raw_now, uint32_t server_ms);
void timebase_tick(timebase_t *tb, uint32_t raw_now);
int32_t timebase_pending(const timebase_t *tb);

#endif /* TIMEBASE_H */
