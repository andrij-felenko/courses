// services/event_dispatcher.c
#include "services/event_dispatcher.h"

void event_dispatcher_init(event_dispatcher_t* d, event_queue_t* queue)
{
    if (!d) return;
    d->queue = queue;
    d->sub_count = 0u;
    d->handled = 0u;
    d->unhandled = 0u;
    for (uint8_t i = 0u; i < EVENT_DISPATCHER_MAX_SUBSCRIBERS; ++i) {
        d->subs[i].mask = 0u;
        d->subs[i].handler = NULL;
        d->subs[i].context = NULL;
    }
}

bool event_dispatcher_subscribe(event_dispatcher_t* d, uint32_t mask,
                                event_handler_fn handler, void* context)
{
    if (!d || !handler || mask == 0u) return false;
    if (d->sub_count >= EVENT_DISPATCHER_MAX_SUBSCRIBERS) return false;

    d->subs[d->sub_count].mask = mask;
    d->subs[d->sub_count].handler = handler;
    d->subs[d->sub_count].context = context;
    d->sub_count++;
    return true;
}

bool event_dispatcher_run_once(event_dispatcher_t* d)
{
    if (!d || !d->queue) return false;

    event_t evt;
    if (!event_queue_pop(d->queue, &evt)) {
        return false;
    }

    bool taken = false;
    for (uint8_t i = 0u; i < d->sub_count; ++i) {
        if ((d->subs[i].mask & EVENT_MASK(evt.type)) != 0u) {
            d->subs[i].handler(d->subs[i].context, &evt);
            taken = true;
        }
    }

    if (taken) {
        d->handled++;
    } else {
        // Подія без жодного підписника — не помилка, але привід глянути в діагностику.
        d->unhandled++;
    }
    return true;
}

uint32_t event_dispatcher_drain(event_dispatcher_t* d)
{
    uint32_t n = 0u;
    // Обробник може покласти в чергу нову подію (тривога породжує скидання живлення),
    // тому цикл іде до справжнього спорожнення, а не на знімок довжини.
    while (event_dispatcher_run_once(d)) {
        n++;
        if (n > (uint32_t)EVENT_QUEUE_CAPACITY * 4u) {
            // Запобіжник від нескінченного самопородження подій.
            break;
        }
    }
    return n;
}
