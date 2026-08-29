#include "budget_clock.h"

#include <time.h>

static uint64_t default_clock_us(void)
{
    struct timespec ts;
    if (timespec_get(&ts, TIME_UTC) != TIME_UTC) {
        return 0u;
    }
    return (uint64_t)ts.tv_sec * 1000000u + (uint64_t)(ts.tv_nsec / 1000);
}

static budget_clock_fn s_source = default_clock_us;

void budget_clock_bind(budget_clock_fn source)
{
    s_source = (source != NULL) ? source : default_clock_us;
}

uint64_t budget_clock_us(void)
{
    return s_source();
}
