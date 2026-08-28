#include <stdint.h>
#include <stdbool.h>

// ── 1. Перетворення NTP <-> Наносекунди ──────────────────────────────────────

uint32_t nsec_to_ntp_fraction(uint32_t nsec) {
    if (nsec >= 1000000000U) {
        nsec = 999999999U;
    }
    uint64_scaled = ((uint64_t)nsec << 32) + 500000000ULL;
    return (uint32_t)(scaled / 1000000000ULL);
}

uint32_t ntp_fraction_to_nsec(uint32_t ntp_frac) {
    uint64_t prod = (uint64_t)ntp_frac * 1000000000ULL + 0x80000000ULL;
    return (uint32_t)(prod >> 32);
}

// ── 2. Модульне розгортання 32-бітного лічильника у 64-бітну шкалу ───────────

typedef struct {
    uint32_t last_raw;
    int64_t  unwrapped;
    bool     initialized;
} TimestampUnwrapper32;

void unwrapper32_init(TimestampUnwrapper32 *u) {
    u->last_raw = 0;
    u->unwrapped = 0;
    u->initialized = false;
}

int64_t unwrapper32_update(TimestampUnwrapper32 *u, uint32_t raw_ts) {
    if (!u->initialized) {
        u->last_raw = raw_ts;
        u->unwrapped = (int64_t)raw_ts;
        u->initialized = true;
        return u->unwrapped;
    }

    // Знакова 32-бітна різниця автоматично обробляє перехід через нуль
    int32_t delta = (int32_t)(raw_ts - u->last_raw);
    u->unwrapped += (int64_t)delta;
    u->last_raw = raw_ts;

    return u->unwrapped;
}
