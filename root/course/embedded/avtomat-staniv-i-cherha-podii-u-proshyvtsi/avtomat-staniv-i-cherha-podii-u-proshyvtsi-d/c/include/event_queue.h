#ifndef EVSE_EVENT_QUEUE_H
#define EVSE_EVENT_QUEUE_H

#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

#include "evse_events.h"

/*
 * Розмір мусить бути степенем двійки: тоді перенесення індексу через край
 * робиться бітовою маскою & (SIZE - 1) замість ділення з остачею, яке на
 * Cortex-M0 коштує десятки тактів у програмній підпрограмі.
 */
#define EVENT_QUEUE_SIZE 16u
#define EVENT_QUEUE_MASK (EVENT_QUEUE_SIZE - 1u)

_Static_assert((EVENT_QUEUE_SIZE & EVENT_QUEUE_MASK) == 0u,
               "розмір черги мусить бути степенем двійки");

typedef struct {
    event_t          slot[EVENT_QUEUE_SIZE];
    _Atomic uint16_t head;    /* індекс запису: рухають виробники */
    _Atomic uint16_t tail;    /* індекс читання: рухає лише головний цикл */
    _Atomic uint16_t dropped; /* скільки подій утрачено через переповнення */
} event_queue_t;

void event_queue_init(event_queue_t *q);

/*
 * Постановка події. Викликається з обробників переривань, тому всередині сама
 * бере критичну секцію: виробників у нас кілька (кнопка, таймер, UART,
 * компаратор), і на різних рівнях пріоритету NVIC один може витіснити іншого
 * рівно між читанням head і його записом.
 */
bool event_queue_push(event_queue_t *q, uint16_t id, uint16_t param);

/* Вибирання події. Викликається виключно з головного циклу. */
bool event_queue_pop(event_queue_t *q, event_t *out);

bool     event_queue_is_empty(event_queue_t *q);
uint16_t event_queue_dropped(event_queue_t *q);

/* Єдина черга системи: одна на всю прошивку, споживач у неї теж один. */
extern event_queue_t g_events;

#endif /* EVSE_EVENT_QUEUE_H */
