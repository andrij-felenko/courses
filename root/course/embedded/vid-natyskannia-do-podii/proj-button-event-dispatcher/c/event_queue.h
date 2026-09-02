#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <stdbool.h>
#include <stdint.h>

#include "input_event.h"

/* Місткість МУСИТЬ бути степенем двійки: індекс згортається маскою, а не
   діленням — ділення в контексті переривання ми собі не дозволяємо. */
#define EVENT_QUEUE_SIZE 16u
#define EVENT_QUEUE_MASK (EVENT_QUEUE_SIZE - 1u)

/* Класична SPSC-черга (Single Producer, Single Consumer):
   head рухає ЛИШЕ продюсер (переривання таймера), tail — ЛИШЕ споживач
   (головний цикл). Спільного лічильника count немає, тому й критична секція
   з __disable_irq() тут не потрібна: кожен індекс має одного власника. */
typedef struct {
    input_event_t     buffer[EVENT_QUEUE_SIZE];
    volatile uint8_t  head;
    volatile uint8_t  tail;
    volatile uint16_t dropped;  /* скільки подій відкинуто через переповнення */
} event_queue_t;

void     queue_init(event_queue_t *q);
bool     queue_push(event_queue_t *q, input_event_t evt);  /* контекст ISR */
bool     queue_pop(event_queue_t *q, input_event_t *evt);  /* контекст main */
void     queue_clear(event_queue_t *q);                    /* контекст main */
uint8_t  queue_size(const event_queue_t *q);
uint16_t queue_dropped(const event_queue_t *q);

#endif /* EVENT_QUEUE_H */
