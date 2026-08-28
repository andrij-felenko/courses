/* dwt_profiler.c — Реалізація функцій профілювання */
#include "dwt_profiler.h"

static uint32_t s_dwt_overhead = 0;

static void dwt_calibrate_overhead(void) {
    s_dwt_overhead = 0;
    uint32_t total = 0;
    const uint32_t runs = 16;

    for (uint32_t i = 0; i < runs; ++i) {
        __asm__ volatile("" ::: "memory");
        uint32_t t0 = dwt_get_cycles();
        __asm__ volatile("" ::: "memory");
        uint32_t t1 = dwt_get_cycles();
        total += (t1 - t0);
    }
    s_dwt_overhead = total / runs;
}

bool dwt_profiler_init(void) {
#if defined(CoreDebug) && defined(DWT)
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;
    dwt_calibrate_overhead();
    return (DWT->CTRL & DWT_CTRL_CYCCNTENA_Msk) != 0;
#else
    CORE_DEBUG_DEMCR |= DEMCR_TRCENA_BIT;
    DWT_CTRL |= DWT_CYCCNTENA_BIT;
    DWT_CYCCNT = 0;
    dwt_calibrate_overhead();
    return (DWT_CTRL & DWT_CYCCNTENA_BIT) != 0;
#endif
}

uint32_t dwt_elapsed_cycles(uint32_t start_cycles) {
    uint32_t now = dwt_get_cycles();
    uint32_t diff = now - start_cycles;
    return (diff > s_dwt_overhead) ? (diff - s_dwt_overhead) : 0;
}

uint64_t dwt_cycles_to_ns(uint32_t cycles, uint32_t cpu_freq_hz) {
    if (cpu_freq_hz == 0) return 0;
    return ((uint64_t)cycles * 1000000000ULL) / cpu_freq_hz;
}

void profiler_stats_update(profiler_stats_t *stats, uint32_t cycles) {
    if (stats->samples_count == 0) {
        stats->min_cycles = cycles;
        stats->max_cycles = cycles;
    } else {
        if (cycles < stats->min_cycles) stats->min_cycles = cycles;
        if (cycles > stats->max_cycles) stats->max_cycles = cycles;
    }
    stats->total_cycles += cycles;
    stats->samples_count++;
}

void profiler_stats_reset(profiler_stats_t *stats) {
    stats->min_cycles = 0xFFFFFFFFU;
    stats->max_cycles = 0;
    stats->total_cycles = 0;
    stats->samples_count = 0;
}
