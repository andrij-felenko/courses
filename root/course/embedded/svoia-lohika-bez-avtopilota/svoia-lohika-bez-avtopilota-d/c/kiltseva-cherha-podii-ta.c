#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_SIZE 16

typedef struct {
    uint8_t id;
    uint32_t timestamp_ms;
    int32_t payload;
} Event;

typedef struct {
    Event buffer[EVENT_QUEUE_SIZE];
    volatile uint8_t head;
    volatile uint8_t tail;
    volatile uint8_t count;
    uint32_t overflow_drops;
} EventQueue;

void event_queue_init(EventQueue *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->overflow_drops = 0;
}

bool event_queue_post(EventQueue *q, const Event *ev) {
    /* Критична секція для безпеки при виклику з ISR */
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    bool success = false;
    if (q->count < EVENT_QUEUE_SIZE) {
        q->buffer[q->head] = *ev;
        q->head = (uint8_t)((q->head + 1) % EVENT_QUEUE_SIZE);
        q->count++;
        success = true;
    } else {
        q->overflow_drops++;
    }

    if (!primask) {
        __enable_irq();
    }
    return success;
}

bool event_queue_pop(EventQueue *q, Event *out_ev) {
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    bool success = false;
    if (q->count > 0) {
        *out_ev = q->buffer[q->tail];
        q->tail = (uint8_t)((q->tail + 1) % EVENT_QUEUE_SIZE);
        q->count--;
        success = true;
    }

    if (!primask) {
        __enable_irq();
    }
    return success;
}
