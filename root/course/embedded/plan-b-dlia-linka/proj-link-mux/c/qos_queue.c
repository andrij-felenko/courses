#include "qos_queue.h"

#include <string.h>

void rx_ring_init(rx_ring_t *r) {
    memset(r->slots, 0, sizeof(r->slots));
    r->overruns = 0u;
    atomic_init(&r->head, 0u);
    atomic_init(&r->tail, 0u);
}

bool rx_ring_push(rx_ring_t *r, const packet_t *pkt) {
    const uint32_t head = atomic_load_explicit(&r->head, memory_order_relaxed);
    /* acquire: бачимо, скільки задача вже забрала, разом із її записами у слоти */
    const uint32_t tail = atomic_load_explicit(&r->tail, memory_order_acquire);

    if (head - tail >= RX_RING_SLOTS) {
        r->overruns++;   /* кадр гине тут — це чесніше, ніж псувати чергу */
        return false;
    }

    r->slots[head & (RX_RING_SLOTS - 1u)] = *pkt;
    /* release: вміст слота мусить стати видимим раніше за новий head */
    atomic_store_explicit(&r->head, head + 1u, memory_order_release);
    return true;
}

bool rx_ring_pop(rx_ring_t *r, packet_t *out) {
    const uint32_t tail = atomic_load_explicit(&r->tail, memory_order_relaxed);
    const uint32_t head = atomic_load_explicit(&r->head, memory_order_acquire);

    if (head == tail) {
        return false;
    }

    *out = r->slots[tail & (RX_RING_SLOTS - 1u)];
    atomic_store_explicit(&r->tail, tail + 1u, memory_order_release);
    return true;
}

static uint32_t count_of(const tx_queue_t *q) {
    return q->head - q->tail;
}

void tx_queue_init(tx_queue_t *q, packet_t *storage, uint32_t capacity,
                   tx_full_policy_t policy) {
    q->slots    = storage;
    q->capacity = capacity;
    q->mask     = capacity - 1u;   /* степінь двійки, інакше маска бреше */
    q->head     = 0u;
    q->tail     = 0u;
    q->policy   = policy;
    q->dropped  = 0u;
    q->peak     = 0u;
}

uint32_t tx_queue_count(const tx_queue_t *q) {
    return count_of(q);
}

bool tx_queue_push(tx_queue_t *q, const packet_t *pkt) {
    if (count_of(q) >= q->capacity) {
        switch (q->policy) {
        case TX_FULL_REJECT:
            return false;              /* хай застосунок знає, що команда не пішла */
        case TX_FULL_DROP_OLDEST:
            q->tail++;                 /* найстаріші координати вже нікому не треба */
            q->dropped++;
            break;
        case TX_FULL_DROP_NEW:
        default:
            q->dropped++;
            return false;
        }
    }

    q->slots[q->head & q->mask] = *pkt;
    q->head++;
    if (count_of(q) > q->peak) {
        q->peak = count_of(q);
    }
    return true;
}

const packet_t *tx_queue_front(const tx_queue_t *q) {
    if (q->head == q->tail) {
        return NULL;
    }
    return &q->slots[q->tail & q->mask];
}

void tx_queue_pop_front(tx_queue_t *q) {
    if (q->head != q->tail) {
        q->tail++;
    }
}

void tx_queue_flush(tx_queue_t *q) {
    q->dropped += count_of(q);
    q->tail = q->head;
}
