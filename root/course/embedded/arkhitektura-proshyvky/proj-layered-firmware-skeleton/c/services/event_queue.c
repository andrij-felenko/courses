// services/event_queue.c
#include "services/event_queue.h"

#include "hal/hal_critical.h"

void event_queue_init(event_queue_t* q)
{
    if (!q) return;
    q->head = 0u;
    q->tail = 0u;
    q->dropped = 0u;
}

bool event_queue_push(event_queue_t* q, const event_t* evt)
{
    if (!q || !evt) return false;

    // Push викликають і головний цикл, і ISR — індекси правимо неподільно.
    const hal_critical_state_t state = hal_critical_enter();

    const uint8_t next_head = (uint8_t)((q->head + 1u) % EVENT_QUEUE_CAPACITY);
    if (next_head == q->tail) {
        // Черга повна. Подію відкидаємо й лічимо: мовчазна втрата гірша за втрату,
        // яку видно в діагностиці.
        if (q->dropped != UINT16_MAX) {
            q->dropped++;
        }
        hal_critical_exit(state);
        return false;
    }

    q->buffer[q->head] = *evt;
    q->head = next_head;

    hal_critical_exit(state);
    return true;
}

bool event_queue_pop(event_queue_t* q, event_t* evt)
{
    if (!q || !evt) return false;

    const hal_critical_state_t state = hal_critical_enter();

    if (q->tail == q->head) {
        hal_critical_exit(state);
        return false;  // Порожньо
    }

    *evt = q->buffer[q->tail];
    q->tail = (uint8_t)((q->tail + 1u) % EVENT_QUEUE_CAPACITY);

    hal_critical_exit(state);
    return true;
}

bool event_queue_is_empty(const event_queue_t* q)
{
    if (!q) return true;
    const hal_critical_state_t state = hal_critical_enter();
    const bool empty = (q->head == q->tail);
    hal_critical_exit(state);
    return empty;
}

uint8_t event_queue_count(const event_queue_t* q)
{
    if (!q) return 0u;
    const hal_critical_state_t state = hal_critical_enter();
    const uint8_t head = q->head;
    const uint8_t tail = q->tail;
    hal_critical_exit(state);
    return (uint8_t)((head + EVENT_QUEUE_CAPACITY - tail) % EVENT_QUEUE_CAPACITY);
}

uint16_t event_queue_dropped(const event_queue_t* q)
{
    return q ? q->dropped : 0u;
}
