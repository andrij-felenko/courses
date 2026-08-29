#include "timebase.h"

void timebase_init(timebase_t *tb, uint32_t raw_now) {
    tb->offset_ms = 0;
    tb->pending_ms = 0;
    tb->last_raw_ms = raw_now;
}

uint32_t timebase_now(const timebase_t *tb, uint32_t raw_now) {
    return (uint32_t)((int32_t)raw_now + tb->offset_ms);
}

void timebase_set_reference(timebase_t *tb, uint32_t raw_now, uint32_t server_ms) {
    // Різницю не застосовуємо стрибком — лише ставимо в чергу на підтягування.
    tb->pending_ms = (int32_t)(server_ms - timebase_now(tb, raw_now));
}

void timebase_tick(timebase_t *tb, uint32_t raw_now) {
    uint32_t dt = raw_now - tb->last_raw_ms;
    tb->last_raw_ms = raw_now;
    if (dt == 0U || tb->pending_ms == 0) return;

    int32_t step = (int32_t)((dt * (uint32_t)TIMEBASE_SLEW_PERCENT) / 100U);
    if (step == 0) step = 1;   // за дуже короткий такт рухаємось хоча б на мілісекунду

    if (tb->pending_ms > 0) {
        if (step > tb->pending_ms) step = tb->pending_ms;
        tb->offset_ms += step;
        tb->pending_ms -= step;
    } else {
        if (step > -tb->pending_ms) step = -tb->pending_ms;
        tb->offset_ms -= step;
        tb->pending_ms += step;
    }
}

int32_t timebase_pending(const timebase_t *tb) { return tb->pending_ms; }
