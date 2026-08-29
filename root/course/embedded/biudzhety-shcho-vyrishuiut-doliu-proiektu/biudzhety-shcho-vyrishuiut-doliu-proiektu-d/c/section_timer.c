#include "section_timer.h"

#include "budget_clock.h"

#include <string.h>

bool section_timer_init(section_timer_t *timer, const char *name,
                        uint32_t deadline_us)
{
    if (timer == NULL || name == NULL || deadline_us == 0u) {
        return false;
    }
    memset(timer, 0, sizeof *timer);
    timer->name        = name;
    timer->deadline_us = deadline_us;
    return true;
}

void section_timer_begin(section_timer_t *timer)
{
    if (timer == NULL || timer->active) {
        /* Вкладений вимір тієї самої секції зіпсував би облік. */
        return;
    }
    timer->started_us = budget_clock_us();
    timer->active     = true;
}

uint32_t section_timer_end(section_timer_t *timer)
{
    if (timer == NULL || !timer->active) {
        return 0u;
    }

    uint64_t elapsed = budget_clock_us() - timer->started_us;
    timer->active    = false;

    uint32_t elapsed_us = (elapsed > UINT32_MAX) ? UINT32_MAX : (uint32_t)elapsed;

    timer->last_us = elapsed_us;
    timer->total_us += elapsed_us;
    timer->runs++;

    if (elapsed_us > timer->worst_us) {
        timer->worst_us = elapsed_us;
    }
    if (elapsed_us > timer->deadline_us) {
        timer->overruns++;
    }
    return elapsed_us;
}

uint32_t section_timer_average_us(const section_timer_t *timer)
{
    if (timer == NULL || timer->runs == 0u) {
        return 0u;
    }
    return (uint32_t)(timer->total_us / timer->runs);
}

int32_t section_timer_margin_us(const section_timer_t *timer)
{
    if (timer == NULL) {
        return 0;
    }
    return (int32_t)timer->deadline_us - (int32_t)timer->worst_us;
}

budget_flags_t section_timer_audit(const section_timer_t *timers, size_t count,
                                   size_t *worst_index)
{
    if (timers == NULL || count == 0u) {
        return BUDGET_OK;
    }

    budget_flags_t flags        = BUDGET_OK;
    int32_t        worst_margin = INT32_MAX;
    size_t         worst        = 0u;

    for (size_t i = 0; i < count; ++i) {
        if (timers[i].overruns > 0u) {
            flags |= BUDGET_DEADLINE_MISS;
        }

        int32_t margin = section_timer_margin_us(&timers[i]);
        if (timers[i].runs > 0u && margin < worst_margin) {
            worst_margin = margin;
            worst        = i;
        }
    }

    if (worst_index != NULL) {
        *worst_index = worst;
    }
    return flags;
}
