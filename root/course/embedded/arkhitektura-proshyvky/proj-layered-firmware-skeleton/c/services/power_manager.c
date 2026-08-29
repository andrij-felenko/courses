// services/power_manager.c
#include "services/power_manager.h"

#include <stddef.h>

void power_manager_init(power_manager_t* pm, bsp_power_t* rail, hal_time_t time,
                        uint32_t min_interval_ms)
{
    if (!pm) return;
    pm->rail = rail;
    pm->time = time;
    pm->reinit = NULL;
    pm->reinit_context = NULL;
    pm->on_recovered = NULL;
    pm->recovered_context = NULL;
    pm->min_interval_ms = min_interval_ms;
    pm->last_cycle_ms = 0u;
    pm->cycled_once = false;
    pm->cycles_done = 0u;
    pm->cycles_failed = 0u;
    pm->cycles_suppressed = 0u;
}

void power_manager_set_reinit(power_manager_t* pm, power_manager_reinit_fn fn, void* context)
{
    if (!pm) return;
    pm->reinit = fn;
    pm->reinit_context = context;
}

void power_manager_set_recovered(power_manager_t* pm, power_manager_recovered_fn fn, void* context)
{
    if (!pm) return;
    pm->on_recovered = fn;
    pm->recovered_context = context;
}

void power_manager_event_handler(void* context, const event_t* evt)
{
    power_manager_t* pm = (power_manager_t*)context;
    if (!pm || !evt || !pm->rail) return;
    if (evt->type != EVT_SENSOR_FAULT) return;

    if (pm->cycled_once && hal_time_elapsed_ms(&pm->time, pm->last_cycle_ms) < pm->min_interval_ms) {
        // Скидати живлення частіше, ніж давач встигає піднятись, — це не лікування,
        // а самопідтримний цикл відмов.
        pm->cycles_suppressed++;
        return;
    }

    pm->last_cycle_ms = hal_time_now_ms(&pm->time);
    pm->cycled_once = true;

    if (!bsp_power_cycle_sensors(pm->rail)) {
        pm->cycles_failed++;
        return;
    }

    if (pm->reinit && !pm->reinit(pm->reinit_context)) {
        // Живлення повернули, але давач не піднявся. Наступна невдача опитування
        // дасть нову подію несправності — і нову спробу, вже після витримки.
        pm->cycles_failed++;
        return;
    }

    pm->cycles_done++;
    if (pm->on_recovered) {
        pm->on_recovered(pm->recovered_context);
    }
}

bool power_manager_attach(power_manager_t* pm, event_dispatcher_t* dispatcher)
{
    if (!pm || !dispatcher) return false;
    return event_dispatcher_subscribe(dispatcher, EVENT_MASK(EVT_SENSOR_FAULT),
                                      power_manager_event_handler, pm);
}
