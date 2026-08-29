// services/event_queue.h — кільцева черга подій, брокер повідомлень усередині прошивки.
#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EVT_NONE = 0,
    EVT_TIMER_TICK,         // Періодичний тик від SysTick
    EVT_SENSOR_TRIGGER,     // Час опитати давач
    EVT_ALERT_THRESHOLD,    // Температура перевищила поріг тривоги
    EVT_SENSOR_FAULT,       // Давач не відповідає кілька спроб поспіль
    EVT_RADIO_TX_COMPLETE   // Передавач звільнився
} event_type_t;

typedef struct {
    event_type_t type;
    uint32_t timestamp_ms;
    union {
        float sensor_val;
        int32_t error_code;
    } payload;
} event_t;

// Ємність — стала часу компіляції, памʼять під чергу статична.
#define EVENT_QUEUE_CAPACITY 16u

typedef struct {
    event_t buffer[EVENT_QUEUE_CAPACITY];
    volatile uint8_t head;      // Куди пишемо
    volatile uint8_t tail;      // Звідки читаємо
    volatile uint16_t dropped;  // Скільки подій відкинуто через переповнення
} event_queue_t;

void event_queue_init(event_queue_t* q);

// Обидві операції безпечні для виклику з обробника переривання:
// індекси правляться під критичною секцією.
bool event_queue_push(event_queue_t* q, const event_t* evt);
bool event_queue_pop(event_queue_t* q, event_t* evt);

bool event_queue_is_empty(const event_queue_t* q);
uint8_t event_queue_count(const event_queue_t* q);
uint16_t event_queue_dropped(const event_queue_t* q);

#endif  // EVENT_QUEUE_H
