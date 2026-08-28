#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_CAPACITY 32

typedef struct {
    event_t ring[EVENT_QUEUE_CAPACITY];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    uint8_t max_usage;  // Пікове заповнення черги для діагностики
} event_queue_t;

void event_queue_init(event_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->max_usage = 0;
}

// Захист критичної секції для ядер ARM Cortex-M
static inline uint32_t enter_critical(void) {
    uint32_t primask;
    __asm__ volatile (
        "mrs %0, primask\n"
        "cpsid i\n"
        : "=r" (primask) :: "memory"
    );
    return primask;
}

static inline void exit_critical(uint32_t primask) {
    __asm__ volatile (
        "msr primask, %0\n"
        ::: "memory"
    );
}

bool event_queue_push(event_queue_t *q, const event_t *e) {
    uint32_t state = enter_critical();

    if (q->count >= EVENT_QUEUE_CAPACITY) {
        exit_critical(state);
        // Переповнення черги — фатальний дефект таймінгу
        return false;
    }

    q->ring[q->head] = *e;
    q->head = (uint8_t)((q->head + 1) % EVENT_QUEUE_CAPACITY);
    q->count++;

    if (q->count > q->max_usage) {
        q->max_usage = q->count;
    }

    exit_critical(state);
    return true;
}

bool event_queue_pop(event_queue_t *q, event_t *out_e) {
    uint32_t state = enter_critical();

    if (q->count == 0) {
        exit_critical(state);
        return false;
    }

    *out_e = q->ring[q->tail];
    q->tail = (uint8_t)((q->tail + 1) % EVENT_QUEUE_CAPACITY);
    q->count--;

    exit_critical(state);
    return true;
}
