/* services/event_queue.c — реалізація черги подій.
 * Критична секція тут коротка навмисно: усередині лише копіювання
 * шістнадцяти байтів і зсув індексу. Що довша заборона переривань,
 * то більше тремтіння в реакції на апаратні події. */
#include "services/event_queue.h"

#include "hal/hal_critical.h"

bool event_queue_init(event_queue_t *q, sys_event_t *storage, size_t capacity)
{
    if (q == 0) {
        return false;
    }
    q->dropped    = 0u;
    q->high_water = 0u;
    return ring_buffer_init(&q->rb, storage, sizeof(sys_event_t), capacity);
}

static bool queue_push_locked(event_queue_t *q, const sys_event_t *evt)
{
    const uint32_t state = hal_critical_enter();

    const bool ok = ring_buffer_push(&q->rb, evt);
    if (ok) {
        const uint32_t used = (uint32_t)ring_buffer_count(&q->rb);
        if (used > q->high_water) {
            q->high_water = used;
        }
    } else {
        /* Переповнення черги — не дрібниця: воно означає, що головний цикл
         * не встигає за подіями. Лічильник видно в телеметрії, і саме за ним
         * ловлять надто важкий обробник, який з'їв запас часу. */
        q->dropped++;
    }

    hal_critical_exit(state);
    return ok;
}

bool event_queue_post(event_queue_t *q, const sys_event_t *evt)
{
    if (q == 0 || evt == 0) {
        return false;
    }
    return queue_push_locked(q, evt);
}

bool event_queue_post_from_isr(event_queue_t *q, const sys_event_t *evt)
{
    if (q == 0 || evt == 0) {
        return false;
    }
    return queue_push_locked(q, evt);
}

bool event_queue_pop(event_queue_t *q, sys_event_t *out_evt)
{
    if (q == 0 || out_evt == 0) {
        return false;
    }

    const uint32_t state = hal_critical_enter();
    const bool ok = ring_buffer_pop(&q->rb, out_evt);
    hal_critical_exit(state);
    return ok;
}

size_t event_queue_count(event_queue_t *q)
{
    if (q == 0) {
        return 0u;
    }
    const uint32_t state = hal_critical_enter();
    const size_t n = ring_buffer_count(&q->rb);
    hal_critical_exit(state);
    return n;
}

uint32_t event_queue_dropped(const event_queue_t *q)
{
    return (q != 0) ? q->dropped : 0u;
}

uint32_t event_queue_high_water(const event_queue_t *q)
{
    return (q != 0) ? q->high_water : 0u;
}

const char *sys_event_name(event_id_t id)
{
    switch (id) {
    case EVT_ID_NONE:             return "NONE";
    case EVT_ID_TICK_100MS:       return "TICK";
    case EVT_ID_BUTTON_CLICK:     return "BUTTON";
    case EVT_ID_SENSOR_DATA_READY:return "SENSOR_DATA";
    case EVT_ID_SENSOR_FAULT:     return "SENSOR_FAULT";
    case EVT_ID_ALARM_OVERTEMP:   return "ALARM_TEMP";
    case EVT_ID_ALARM_VIBRATION:  return "ALARM_VIB";
    case EVT_ID_ALARM_CLEARED:    return "ALARM_CLEARED";
    case EVT_ID_COMMS_PACKET_RX:  return "PACKET_RX";
    default:                      return "?";
    }
}
