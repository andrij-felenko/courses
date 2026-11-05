#include <stdint.h>
#include <stdbool.h>

typedef enum {
    TIME_STATE_UNSYNCED = 0,
    TIME_STATE_SYNCED,
    TIME_STATE_SLEWING
} time_sync_state_t;

typedef struct {
    volatile int64_t offset_ms;
    volatile time_sync_state_t state;
} time_subsystem_t;

static time_subsystem_t g_time_sys = {0, TIME_STATE_UNSYNCED};

uint64_t time_get_uptime_ms(void);

uint64_t time_get_wall_clock_ms(void) {
    uint64_t up = time_get_uptime_ms();
    int64_t offset;

    // Критична секція для атомарного зчитування 64-бітного offset на 32-бітній архітектурі
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    offset = g_time_sys.offset_ms;
    if (!primask) __enable_irq();

    return (uint64_t)((int64_t)up + offset);
}

void time_set_utc_ms(uint64_t utc_ms) {
    uint64_t up = time_get_uptime_ms();
    int64_t new_offset = (int64_t)utc_ms - (int64_t)up;

    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    g_time_sys.offset_ms = new_offset;
    g_time_sys.state = TIME_STATE_SYNCED;
    if (!primask) __enable_irq();
}
