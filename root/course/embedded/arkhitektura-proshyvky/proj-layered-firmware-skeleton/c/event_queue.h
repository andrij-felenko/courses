// services/event_queue.h
#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EVT_NONE = 0,
    EVT_TIMER_TICK,
    EVT_SENSOR_TRIGGER,
    EVT_ALERT_THRESHOLD,
    EVT_RADIO_TX_COMPLETE
} event_type_t;

typedef struct {
    event_type_t type;
    uint32_t timestamp_ms;
    union {
        float sensor_val;
        int32_t error_code;
    } payload;
} event_t;

#define EVENT_QUEUE_CAPACITY 16

typedef struct {
    event_t buffer[EVENT_QUEUE_CAPACITY];
    volatile uint8_t head;
    volatile uint8_t tail;
} event_queue_t;

void event_queue_init(event_queue_t* q);
bool event_queue_push(event_queue_t* q, const event_t* evt);
bool event_queue_pop(event_queue_t* q, event_t* evt);

#endif // EVENT_QUEUE_H
