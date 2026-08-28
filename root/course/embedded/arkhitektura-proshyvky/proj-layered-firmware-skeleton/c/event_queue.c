// services/event_queue.c
#include "services/event_queue.h"

void event_queue_init(event_queue_t* q) {
    if (!q) return;
    q->head = 0;
    q->tail = 0;
}

bool event_queue_push(event_queue_t* q, const event_t* evt) {
    if (!q || !evt) return false;
    uint8_t next_head = (q->head + 1) % EVENT_QUEUE_CAPACITY;
    if (next_head == q->tail) {
        return false; // Буфер переповнений, подія відкидається для запобігання пошкодженню пам'яті
    }
    q->buffer[q->head] = *evt;
    q->head = next_head;
    return true;
}

bool event_queue_pop(event_queue_t* q, event_t* evt) {
    if (!q || !evt || q->tail == q->head) {
        return false; // Черга порожня
    }
    *evt = q->buffer[q->tail];
    q->tail = (q->tail + 1) % EVENT_QUEUE_CAPACITY;
    return true;
}
