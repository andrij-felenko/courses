/* systick_counter.c — вимір тривалості спадним 24-бітним SysTick. */
#include "systick_counter.h"

#include <stdbool.h>

static uint32_t s_overhead;

static uint32_t calibrate_overhead(void) {
    uint32_t best = 0xFFFFFFFFU;

    for (int i = 0; i < 32; ++i) {
        __asm__ volatile("" ::: "memory");
        const uint32_t v0 = SYSTICK_VAL;
        __asm__ volatile("" ::: "memory");
        const uint32_t v1 = SYSTICK_VAL;

        const uint32_t delta = v0 - v1; /* рахує вниз, тому v0 більше */
        if (delta < best) {
            best = delta;
        }
    }
    return best;
}

void systick_counter_init(void) {
    SYSTICK_CTRL = 0U;                 /* зупинити на час переналаштування */
    SYSTICK_LOAD = SYSTICK_MAX_LOAD;   /* найдовший період: 2^24 тактів */
    SYSTICK_VAL = 0U;                  /* будь-який запис скидає лічильник і COUNTFLAG */
    SYSTICK_CTRL = SYSTICK_ENABLE | SYSTICK_CLKSOURCE; /* від HCLK, без переривання */

    (void)SYSTICK_CTRL; /* читання гасить COUNTFLAG від пуску */
    s_overhead = calibrate_overhead();
}

uint32_t systick_get_value(void) {
    (void)SYSTICK_CTRL; /* чистимо прапорець ПЕРЕД заміром, інакше побачимо чужий оберт */
    return SYSTICK_VAL;
}

uint32_t systick_elapsed_cycles(uint32_t start_val) {
    const uint32_t now = SYSTICK_VAL;

    /* Читання CTRL і скидає, і повертає COUNTFLAG — тому робимо його рівно раз. */
    const bool wrapped = (SYSTICK_CTRL & SYSTICK_COUNTFLAG) != 0U;
    const uint32_t period = SYSTICK_LOAD + 1U;

    uint32_t elapsed;
    if (!wrapped) {
        elapsed = start_val - now;
    } else {
        /* Один оберт: дорахували від start_val до нуля й далі від LOAD до now.
           Другого обертання прапорець не розрізняє — на 48 МГц межа заміру
           це ≈ 349 мс, і довші ділянки цим лічильником просто не міряють. */
        elapsed = start_val + (period - now);
    }

    return (elapsed > s_overhead) ? (elapsed - s_overhead) : 0U;
}

uint32_t systick_counter_overhead(void) {
    return s_overhead;
}
