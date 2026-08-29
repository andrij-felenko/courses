#include "event_queue.h"

#include "hal.h"

event_queue_t g_events;

void event_queue_init(event_queue_t *q)
{
    atomic_store_explicit(&q->head, 0u, memory_order_relaxed);
    atomic_store_explicit(&q->tail, 0u, memory_order_relaxed);
    atomic_store_explicit(&q->dropped, 0u, memory_order_relaxed);
}

bool event_queue_push(event_queue_t *q, uint16_t id, uint16_t param)
{
    /*
     * Критична секція коротка: заборона переривань триває рівно стільки, щоб
     * скопіювати вісім байтів і зсунути індекс, — одиниці мікросекунд навіть
     * на 8-мегагерцевому ядрі.
     */
    const uint32_t saved = hal_irq_save();

    const uint16_t head      = atomic_load_explicit(&q->head, memory_order_relaxed);
    const uint16_t next_head = (uint16_t)((head + 1u) & EVENT_QUEUE_MASK);

    if (next_head == atomic_load_explicit(&q->tail, memory_order_acquire)) {
        /*
         * Переповнення. Мовчки затирати найстарішу подію не можна: у ній міг
         * бути перехід у стан аварії. Тому подію відкидаємо, лічильник
         * нарощуємо — головний цикл побачить утрату й піде в FAULT.
         */
        const uint16_t lost = atomic_load_explicit(&q->dropped, memory_order_relaxed);
        if (lost != UINT16_MAX) {
            atomic_store_explicit(&q->dropped, (uint16_t)(lost + 1u), memory_order_relaxed);
        }
        hal_irq_restore(saved);
        return false;
    }

    q->slot[head].id    = id;
    q->slot[head].param = param;
    q->slot[head].t_ms  = hal_millis();

    /*
     * Запис-звільнення: усі три поля слоту мусять стати видимими до того, як
     * споживач побачить новий head, інакше він прочитає напівзаповнений запис.
     */
    atomic_store_explicit(&q->head, next_head, memory_order_release);

    hal_irq_restore(saved);
    return true;
}

bool event_queue_pop(event_queue_t *q, event_t *out)
{
    const uint16_t tail = atomic_load_explicit(&q->tail, memory_order_relaxed);

    if (tail == atomic_load_explicit(&q->head, memory_order_acquire)) {
        return false; /* черга порожня */
    }

    *out = q->slot[tail];

    /*
     * Звільнення tail після копіювання: доти виробник не має права вважати
     * слот вільним і перезаписувати його новою подією.
     */
    atomic_store_explicit(&q->tail, (uint16_t)((tail + 1u) & EVENT_QUEUE_MASK),
                          memory_order_release);
    return true;
}

bool event_queue_is_empty(event_queue_t *q)
{
    return atomic_load_explicit(&q->head, memory_order_acquire) ==
           atomic_load_explicit(&q->tail, memory_order_relaxed);
}

uint16_t event_queue_dropped(event_queue_t *q)
{
    return atomic_load_explicit(&q->dropped, memory_order_relaxed);
}
