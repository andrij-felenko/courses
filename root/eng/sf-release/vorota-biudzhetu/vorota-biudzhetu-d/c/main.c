#include <stdint.h>
#include <stdbool.h>

#define DWT_CTRL   (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004U)
#define DEM_CR     (*(volatile uint32_t *)0xE000EDFCU)

typedef enum {
    BOOT_STAGE_RESET = 0,
    BOOT_STAGE_SYSINIT_DONE,
    BOOT_STAGE_STATIC_INIT_DONE,
    BOOT_STAGE_DRIVERS_READY,
    BOOT_STAGE_FIRST_FRAME_SENT,
    BOOT_STAGE_COUNT
} boot_stage_t;

typedef struct {
    uint32_t timestamp_cycles[BOOT_STAGE_COUNT];
    uint32_t cpu_frequency_hz;
} boot_metrics_t;

static boot_metrics_t g_boot_metrics;

void boot_profiler_init(uint32_t cpu_freq) {
    g_boot_metrics.cpu_frequency_hz = cpu_freq;
    DEM_CR |= (1U << 24);     /* Увімкнення трасування (TRCENA) */
    DWT_CYCCNT = 0;           /* Скидання лічильника циклів */
    DWT_CTRL |= (1U << 0);     /* Старт лічильника CYCCNT */
    g_boot_metrics.timestamp_cycles[BOOT_STAGE_RESET] = 0;
}

void boot_profiler_mark(boot_stage_t stage) {
    if (stage < BOOT_STAGE_COUNT) {
        g_boot_metrics.timestamp_cycles[stage] = DWT_CYCCNT;
    }
}

uint32_t boot_profiler_get_duration_us(boot_stage_t stage) {
    if (stage >= BOOT_STAGE_COUNT || g_boot_metrics.cpu_frequency_hz == 0) {
        return 0;
    }
    uint64_t cycles = g_boot_metrics.timestamp_cycles[stage];
    return (uint32_t)((cycles * 1000000ULL) / g_boot_metrics.cpu_frequency_hz);
}
