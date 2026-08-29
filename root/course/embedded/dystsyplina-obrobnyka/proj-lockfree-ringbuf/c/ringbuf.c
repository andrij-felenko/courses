#include "ringbuf.h"

void rb_init(rb_t *rb) {
    rb->head = 0u;
    rb->tail = 0u;
    rb->dropped = 0u;
    rb_barrier();
}

bool rb_push_isr(rb_t *rb, uint8_t byte) {
    const uint32_t head = rb->head;   /* власний індекс: читання точне */
    const uint32_t tail = rb->tail;   /* чужий: міг лише зрости, тобто звільнити місце,
                                         тож застаріле значення дає хибне «повно»,
                                         але ніколи не дає хибного «є місце» */
    const uint32_t next = (head + 1u) & RB_MASK;

    if (next == tail) {
        rb->dropped++;   /* переповнення. В обробнику не чекають — рахують втрату */
        return false;
    }

    rb->storage[head] = byte;

    /* Дані мусять лягти в пам'ять ДО публікації нового head, інакше споживач
       побачить індекс і прочитає з комірки старе сміття. */
    rb_barrier();

    rb->head = next;
    return true;
}

size_t rb_push_isr_burst(rb_t *rb, const uint8_t *data, size_t len) {
    uint32_t head = rb->head;
    const uint32_t tail = rb->tail;
    size_t written = 0u;

    while (written < len) {
        const uint32_t next = (head + 1u) & RB_MASK;
        if (next == tail) {
            break;   /* місце скінчилося: решту пачки втрачено */
        }
        rb->storage[head] = data[written];
        head = next;
        written++;
    }

    if (written != 0u) {
        rb_barrier();      /* один бар'єр на всю пачку, а не на кожен байт */
        rb->head = head;
    }
    rb->dropped += (uint32_t)(len - written);
    return written;
}

uint32_t rb_dropped(const rb_t *rb) {
    return rb->dropped;
}

bool rb_pop(rb_t *rb, uint8_t *out) {
    const uint32_t tail = rb->tail;
    const uint32_t head = rb->head;

    if (tail == head) {
        return false;   /* порожньо */
    }

    /* Побачили новий head — лише після цього читаємо комірку (acquire). */
    rb_barrier();
    *out = rb->storage[tail];

    /* Байт скопійовано ДО того, як слот оголошено вільним (release):
       інакше обробник перепише комірку, яку ми ще не забрали. */
    rb_barrier();
    rb->tail = (tail + 1u) & RB_MASK;
    return true;
}

size_t rb_pop_burst(rb_t *rb, uint8_t *out, size_t max) {
    uint32_t tail = rb->tail;
    const uint32_t head = rb->head;

    size_t ready = (size_t)((head - tail) & RB_MASK);
    if (ready == 0u) {
        return 0u;
    }
    rb_barrier();

    if (ready > max) {
        ready = max;
    }
    for (size_t i = 0u; i < ready; i++) {
        out[i] = rb->storage[tail];
        tail = (tail + 1u) & RB_MASK;
    }

    rb_barrier();
    rb->tail = tail;
    return ready;
}

size_t rb_discard_oldest(rb_t *rb, size_t count) {
    const uint32_t tail = rb->tail;
    const size_t ready = (size_t)((rb->head - tail) & RB_MASK);
    const size_t drop = (count < ready) ? count : ready;

    if (drop != 0u) {
        rb->tail = (uint32_t)((tail + drop) & RB_MASK);
    }
    return drop;
}

size_t rb_available(const rb_t *rb) {
    const uint32_t head = rb->head;
    const uint32_t tail = rb->tail;
    return (size_t)((head - tail) & RB_MASK);
}
