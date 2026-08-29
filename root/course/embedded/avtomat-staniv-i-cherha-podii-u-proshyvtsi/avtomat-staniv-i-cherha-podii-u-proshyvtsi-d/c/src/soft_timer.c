#include "soft_timer.h"

#include <stdatomic.h>

#include "event_queue.h"
#include "hal.h"

typedef struct {
    _Atomic uint32_t deadline_ms;
    _Atomic bool     armed;
} soft_timer_t;

static soft_timer_t s_timers[TMR_COUNT];

void soft_timer_init(void)
{
    for (unsigned i = 0; i < (unsigned)TMR_COUNT; ++i) {
        atomic_store_explicit(&s_timers[i].armed, false, memory_order_relaxed);
        atomic_store_explicit(&s_timers[i].deadline_ms, 0u, memory_order_relaxed);
    }
}

void soft_timer_arm(soft_timer_id_t id, uint32_t delay_ms)
{
    if ((unsigned)id >= (unsigned)TMR_COUNT) {
        return;
    }

    /*
     * Термін і прапорець мусять стати видимими для тіку одним шматком: якби
     * переривання вклинилося між ними, воно побачило б зведений таймер зі
     * старим терміном і вистрілило б негайно.
     */
    const uint32_t saved = hal_irq_save();
    atomic_store_explicit(&s_timers[id].deadline_ms, hal_millis() + delay_ms,
                          memory_order_relaxed);
    atomic_store_explicit(&s_timers[id].armed, true, memory_order_relaxed);
    hal_irq_restore(saved);
}

void soft_timer_disarm(soft_timer_id_t id)
{
    if ((unsigned)id < (unsigned)TMR_COUNT) {
        atomic_store_explicit(&s_timers[id].armed, false, memory_order_relaxed);
    }
}

bool soft_timer_is_armed(soft_timer_id_t id)
{
    if ((unsigned)id >= (unsigned)TMR_COUNT) {
        return false;
    }
    return atomic_load_explicit(&s_timers[id].armed, memory_order_relaxed);
}

void soft_timer_tick(uint32_t now_ms)
{
    for (unsigned i = 0; i < (unsigned)TMR_COUNT; ++i) {
        if (!atomic_load_explicit(&s_timers[i].armed, memory_order_relaxed)) {
            continue;
        }

        const uint32_t deadline =
            atomic_load_explicit(&s_timers[i].deadline_ms, memory_order_relaxed);

        /*
         * Порівняння різниці зі знаком, а не «now >= deadline»: лічильник
         * мілісекунд переповнюється кожні 49 діб, і пряме порівняння в цю мить
         * зробило б усі зведені таймери «ще не готовими» на наступні 49 діб.
         */
        if ((int32_t)(now_ms - deadline) >= 0) {
            atomic_store_explicit(&s_timers[i].armed, false, memory_order_relaxed);
            (void)event_queue_push(&g_events, EVT_TIMEOUT, (uint16_t)i);
        }
    }
}
