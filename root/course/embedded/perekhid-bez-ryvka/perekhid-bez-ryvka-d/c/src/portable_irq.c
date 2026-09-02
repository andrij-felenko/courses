#include "portable_irq.h"

static volatile unsigned g_depth = 0u;
static unsigned g_lock_events = 0u;
static unsigned g_deferred_ticks = 0u;

irq_state_t irq_lock(void)
{
    const irq_state_t saved = g_depth;
    g_depth = saved + 1u;
    ++g_lock_events;
    return saved;
}

void irq_unlock(irq_state_t saved)
{
    /* Відновлюємо збережений стан, а не «просто вмикаємо»: вкладені критичні
       секції інакше відкрили б переривання посеред зовнішньої транзакції. */
    g_depth = saved;
}

bool irq_locked(void)
{
    return g_depth > 0u;
}

unsigned irq_lock_events(void)
{
    return g_lock_events;
}

void irq_note_deferred_tick(void)
{
    ++g_deferred_ticks;
}

unsigned irq_deferred_ticks(void)
{
    return g_deferred_ticks;
}

void irq_reset_counters(void)
{
    g_lock_events = 0u;
    g_deferred_ticks = 0u;
}
