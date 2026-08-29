/* services/event_queue.h — черга подій між перериваннями і головним циклом.
 * Це кільцевий буфер плюс критична секція: єдине місце в системі, де
 * переривання зустрічається з прикладним кодом. Усе інше живе на одному боці
 * цієї межі й про перегони не думає. */
#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include "include/event_types.h"
#include "services/ring_buffer.h"

typedef struct event_queue {
    ring_buffer_t     rb;
    volatile uint32_t dropped;      /* події, що не влізли */
    volatile uint32_t high_water;   /* найбільша зайнятість черги */
} event_queue_t;

/* storage — масив подій завдовжки capacity, який дає викликач (статичний). */
bool event_queue_init(event_queue_t *q, sys_event_t *storage, size_t capacity);

/* Публікація з контексту головного циклу. */
bool event_queue_post(event_queue_t *q, const sys_event_t *evt);

/* Публікація з обробника переривання. На Cortex-M тіло те саме, але виклик
 * названо окремо навмисно: у прошивці з ядром RTOS ці дві функції розходяться
 * (FromISR-варіанти API), і назва місця виклику мусить бути видима в коді. */
bool event_queue_post_from_isr(event_queue_t *q, const sys_event_t *evt);

/* Забирає найстарішу подію. false — черга порожня; чекати всередині черга
 * не вміє й не має: сон — справа головного циклу. */
bool event_queue_pop(event_queue_t *q, sys_event_t *out_evt);

size_t   event_queue_count(event_queue_t *q);
uint32_t event_queue_dropped(const event_queue_t *q);
uint32_t event_queue_high_water(const event_queue_t *q);

#endif /* EVENT_QUEUE_H */
