// services/event_dispatcher.h — диспетчер: витягує подію з черги й віддає її
// підписникам. Джерело події не знає, хто її обробить; обробник не знає, хто її породив.
#ifndef EVENT_DISPATCHER_H
#define EVENT_DISPATCHER_H

#include <stddef.h>

#include "services/event_queue.h"

#define EVENT_DISPATCHER_MAX_SUBSCRIBERS 8u

// Маска типів: підписник каже, які події його цікавлять.
#define EVENT_MASK(type) (1u << (unsigned)(type))
#define EVENT_MASK_ALL 0xFFFFFFFFu

typedef void (*event_handler_fn)(void* context, const event_t* evt);

typedef struct {
    uint32_t mask;
    event_handler_fn handler;
    void* context;
} event_subscriber_t;

typedef struct {
    event_queue_t* queue;
    event_subscriber_t subs[EVENT_DISPATCHER_MAX_SUBSCRIBERS];
    uint8_t sub_count;
    uint32_t handled;
    uint32_t unhandled;
} event_dispatcher_t;

void event_dispatcher_init(event_dispatcher_t* d, event_queue_t* queue);

// Повертає false, якщо таблиця підписників уже заповнена — статичний пул,
// динамічної памʼяті в прошивці немає.
bool event_dispatcher_subscribe(event_dispatcher_t* d, uint32_t mask,
                                event_handler_fn handler, void* context);

// Знімає рівно одну подію. Повертає false, коли черга порожня.
bool event_dispatcher_run_once(event_dispatcher_t* d);

// Вичерпує чергу до дна; повертає кількість оброблених подій.
uint32_t event_dispatcher_drain(event_dispatcher_t* d);

#endif  // EVENT_DISPATCHER_H
