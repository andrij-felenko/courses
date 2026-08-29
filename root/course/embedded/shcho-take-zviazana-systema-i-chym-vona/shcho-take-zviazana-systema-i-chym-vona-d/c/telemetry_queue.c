#include "telemetry_queue.h"

#include <string.h>

void telemetry_queue_init(telemetry_queue_t *q)
{
    if (q == NULL) {
        return;
    }
    memset(q, 0, sizeof(*q));
}

bool telemetry_queue_push(telemetry_queue_t *q, const telemetry_entry_t *entry)
{
    bool overwrote = false;

    if ((q == NULL) || (entry == NULL)) {
        return false;
    }

    q->slots[q->head] = *entry;
    q->head = (uint16_t)((q->head + 1u) % TELEMETRY_QUEUE_CAPACITY);

    if (q->count < TELEMETRY_QUEUE_CAPACITY) {
        q->count++;
    } else {
        /* Голова наздогнала хвіст. Пам'ять скінчилася раніше за обрив зв'язку —
           жертвуємо найстарішим виміром: свіжий стан двигуна цінніший за вчорашній. */
        q->tail = (uint16_t)((q->tail + 1u) % TELEMETRY_QUEUE_CAPACITY);
        q->dropped_total++;
        overwrote = true;
    }

    return overwrote;
}

const telemetry_entry_t *telemetry_queue_peek(const telemetry_queue_t *q)
{
    if ((q == NULL) || (q->count == 0u)) {
        return NULL;
    }
    return &q->slots[q->tail];
}

bool telemetry_queue_pop(telemetry_queue_t *q)
{
    if ((q == NULL) || (q->count == 0u)) {
        return false;
    }
    q->tail = (uint16_t)((q->tail + 1u) % TELEMETRY_QUEUE_CAPACITY);
    q->count--;
    return true;
}

uint16_t telemetry_queue_count(const telemetry_queue_t *q)
{
    return (q == NULL) ? 0u : q->count;
}

bool telemetry_queue_empty(const telemetry_queue_t *q)
{
    return telemetry_queue_count(q) == 0u;
}

uint32_t telemetry_queue_dropped(const telemetry_queue_t *q)
{
    return (q == NULL) ? 0u : q->dropped_total;
}
