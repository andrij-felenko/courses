#include "deadman.h"

#include "platform.h"

void deadman_init(deadman_t *d, uint32_t timeout_ms, uint32_t heartbeat_ms, uint32_t now) {
    d->timeout_ms = timeout_ms;
    d->heartbeat_ms = heartbeat_ms;
    d->deadline_ms = now + timeout_ms;
    d->last_pulse_ms = now;
    d->trips = 0U;
    d->tripped = false;
    plat_pulse_interlock();   // перший імпульс піднімає лінію ENABLE
}

void deadman_feed(deadman_t *d, uint32_t now) {
    d->deadline_ms = now + d->timeout_ms;
    d->tripped = false;
}

bool deadman_expired(const deadman_t *d, uint32_t now) {
    // Порівняння через різницю зі знаком — коректне й після переповнення лічильника.
    return (int32_t)(now - d->deadline_ms) > 0;
}

uint32_t deadman_remaining_ms(const deadman_t *d, uint32_t now) {
    int32_t left = (int32_t)(d->deadline_ms - now);
    return (left > 0) ? (uint32_t)left : 0U;
}

void deadman_service(deadman_t *d, uint32_t now) {
    if (deadman_expired(d, now)) {
        if (!d->tripped) {
            d->tripped = true;
            d->trips++;
        }
        return;   // мовчимо: за INTERLOCK_HOLD_MS супервізор сам зніме ENABLE
    }
    if ((uint32_t)(now - d->last_pulse_ms) >= d->heartbeat_ms) {
        plat_pulse_interlock();
        d->last_pulse_ms = now;
    }
}
