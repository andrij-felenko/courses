#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_SIZE 16
#define EVENT_QUEUE_MASK (EVENT_QUEUE_SIZE - 1)

typedef uint16_t EventId;

typedef struct {
    EventId id;
    uintptr_t payload;
} Event;

typedef struct {
    Event buffer[EVENT_QUEUE_SIZE];
    volatile uint8_t head; // індекс запису (виробник / ISR)
    volatile uint8_t tail; // індекс читання (споживач / main)
} EventQueue;

void event_queue_init(EventQueue *q) {
    q->head = 0;
    q->tail = 0;
}

// Виклик виключно з ISR або з критичної секції
bool event_queue_push(EventQueue *q, EventId id, uintptr_t payload) {
    uint8_t next_head = (q->head + 1) & EVENT_QUEUE_MASK;
    if (next_head == q->tail) {
        // Переповнення черги! Подію втрачено (Backpressure)
        return false;
    }
    q->buffer[q->head].id = id;
    q->buffer[q->head].payload = payload;
    q->head = next_head;
    return true;
}

// Виклик виключно з головного циклу
bool event_queue_pop(EventQueue *q, Event *out_event) {
    if (q->head == q->tail) {
        return false; // Черга порожня
    }
    *out_event = q->buffer[q->tail];
    q->tail = (q->tail + 1) & EVENT_QUEUE_MASK;
    return true;
}
