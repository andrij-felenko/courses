#include <stddef.h>

#include "event_queue.h"

/* Тіло події мусить лягти в пам'ять ДО того, як зміниться head: інакше
   компілятор має право переставити записи, і споживач побачить індекс
   раніше за дані. На одноядерному Cortex-M досить бар'єра компілятора. */
#if defined(__GNUC__) || defined(__clang__)
#  define QUEUE_BARRIER() __atomic_signal_fence(__ATOMIC_SEQ_CST)
#else
#  define QUEUE_BARRIER() do { } while (0)
#endif

void queue_init(event_queue_t *q) {
    if (q == NULL) {
        return;
    }
    q->head = 0;
    q->tail = 0;
    q->dropped = 0;
}

bool queue_push(event_queue_t *q, input_event_t evt) {
    if (q == NULL) {
        return false;
    }

    const uint8_t head = q->head;
    const uint8_t next = (uint8_t)((head + 1u) & EVENT_QUEUE_MASK);

    if (next == q->tail) {
        /* Черга повна: один слот завжди лишається порожнім — це ціна за
           відмову від спільного лічильника. Чекати в перериванні не можна,
           тож подію відкидаємо й лише рахуємо втрату. */
        if (q->dropped < UINT16_MAX) {
            q->dropped++;
        }
        return false;
    }

    q->buffer[head] = evt;
    QUEUE_BARRIER();
    q->head = next;
    return true;
}

bool queue_pop(event_queue_t *q, input_event_t *evt) {
    if (q == NULL || evt == NULL) {
        return false;
    }

    const uint8_t tail = q->tail;
    if (tail == q->head) {
        return false;
    }

    *evt = q->buffer[tail];
    QUEUE_BARRIER();
    q->tail = (uint8_t)((tail + 1u) & EVENT_QUEUE_MASK);
    return true;
}

/* Викидання залишків при зміні екрана. Робить це ТІЛЬКИ споживач: він
   власник tail, тож перегін tail до head безпечний навіть тоді, коли
   переривання саме в цю мить кладе нову подію. queue_init() для того самого
   годиться лише до старту таймера — він чіпає обидва індекси. */
void queue_clear(event_queue_t *q) {
    if (q == NULL) {
        return;
    }
    q->tail = q->head;
}

uint8_t queue_size(const event_queue_t *q) {
    if (q == NULL) {
        return 0;
    }
    /* Різницю згортаємо в uint8_t ДО маски: індекси цілочисельно підвищуються
       до int, і при tail > head віднімання дало б від'ємне число. */
    return (uint8_t)((uint8_t)(q->head - q->tail) & EVENT_QUEUE_MASK);
}

uint16_t queue_dropped(const event_queue_t *q) {
    return (q == NULL) ? 0u : q->dropped;
}
