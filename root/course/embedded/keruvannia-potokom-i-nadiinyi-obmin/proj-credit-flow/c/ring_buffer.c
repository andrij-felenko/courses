#include "ring_buffer.h"

#include <string.h>

/* --- Примітиви ядра ------------------------------------------------------ */

#if defined(__ARM_ARCH)

/* Бар'єр даних: гарантує, що запис байта в storage завершився РАНІШЕ, ніж
 * споживач побачить новий head. Без нього ядро з перевпорядкуванням (Cortex-M7)
 * має право опублікувати індекс раніше за самі дані. */
static inline void rb_dmb(void) { __asm volatile("dmb 0xF" ::: "memory"); }

static inline uint32_t rb_irq_lock(void)
{
    uint32_t primask;
    __asm volatile("mrs %0, primask" : "=r"(primask));
    __asm volatile("cpsid i" ::: "memory");
    return primask;
}

static inline void rb_irq_unlock(uint32_t primask)
{
    /* Відновлюємо, а не вмикаємо наосліп: виклик міг статися вже під замком. */
    if ((primask & 1u) == 0u) {
        __asm volatile("cpsie i" ::: "memory");
    }
}

#else

/* Хостовий прогін демонстрації: справжніх переривань немає, лишається бар'єр
 * компілятора, щоб оптимізатор не переставив записи місцями. */
#include <stdatomic.h>
static inline void rb_dmb(void) { atomic_signal_fence(memory_order_seq_cst); }
static inline uint32_t rb_irq_lock(void)
{
    atomic_signal_fence(memory_order_seq_cst);
    return 0;
}
static inline void rb_irq_unlock(uint32_t saved)
{
    (void)saved;
    atomic_signal_fence(memory_order_seq_cst);
}

#endif

/* --- Внутрішнє ----------------------------------------------------------- */

/* Різниця беззнакових індексів правильна й після переповнення uint32_t. */
static inline uint32_t rb_used(const ring_buffer_t *rb)
{
    return rb->head - rb->tail;
}

/* Перевірку «рівень упав» і зміну стану лінії робимо однією неподільною дією:
 * інакше між читанням рівня й записом прапорця встигає влетіти ISR, підняти
 * Busy — а ми затерли б його своїм Ready і дістали переповнення. */
static void rb_release_line(ring_buffer_t *rb)
{
    uint32_t saved = rb_irq_lock();
    if (!rb->rts_ready && rb_used(rb) <= RB_LOW_WATERMARK) {
        rb->rts_ready = true;
        if (rb->set_rts != NULL) {
            rb->set_rts(true);
        }
    }
    rb_irq_unlock(saved);
}

/* --- Публічний інтерфейс ------------------------------------------------- */

void rb_init(ring_buffer_t *rb, rb_rts_fn set_rts)
{
    memset(rb->storage, 0, sizeof rb->storage);
    rb->head = 0u;
    rb->tail = 0u;
    rb->overruns = 0u;
    rb->set_rts = set_rts;
    rb->rts_ready = true;
    if (rb->set_rts != NULL) {
        rb->set_rts(true);
    }
}

bool rb_push_from_isr(ring_buffer_t *rb, uint8_t byte)
{
    const uint32_t head = rb->head;

    if ((uint32_t)(head - rb->tail) >= RB_CAPACITY) {
        /* Запас уже з'їдено: передавач не спинився вчасно. Байт втрачено —
         * рахуємо це, бо мовчазна втрата на шині виглядає як «глюк» на місяць. */
        rb->overruns++;
        return false;
    }

    rb->storage[head & RB_MASK] = byte;
    rb_dmb(); /* байт у пам'яті раніше, ніж індекс покаже на нього */
    rb->head = head + 1u;

    /* Підняти Busy можна без критичної секції: споживач свою частину робить із
     * вимкненими перериваннями, тож ми ніколи не влітаємо в середину його дії. */
    if (rb->rts_ready && rb_used(rb) >= RB_HIGH_WATERMARK) {
        rb->rts_ready = false;
        if (rb->set_rts != NULL) {
            rb->set_rts(false);
        }
    }
    return true;
}

bool rb_pop(ring_buffer_t *rb, uint8_t *out_byte)
{
    const uint32_t tail = rb->tail;

    if (rb->head == tail) {
        return false;
    }

    *out_byte = rb->storage[tail & RB_MASK];
    rb_dmb(); /* байт прочитано раніше, ніж слот оголошено вільним */
    rb->tail = tail + 1u;

    rb_release_line(rb);
    return true;
}

size_t rb_pop_bulk(ring_buffer_t *rb, uint8_t *dst, size_t max_bytes)
{
    const uint32_t tail = rb->tail;
    uint32_t available = (uint32_t)(rb->head - tail);
    size_t taken;

    if (available > (uint32_t)max_bytes) {
        available = (uint32_t)max_bytes;
    }
    for (taken = 0; taken < available; taken++) {
        dst[taken] = rb->storage[(tail + (uint32_t)taken) & RB_MASK];
    }
    if (taken == 0) {
        return 0;
    }

    rb_dmb();
    rb->tail = tail + (uint32_t)taken;

    rb_release_line(rb);
    return taken;
}

size_t rb_level(const ring_buffer_t *rb)
{
    return (size_t)(rb->head - rb->tail);
}

size_t rb_free_space(const ring_buffer_t *rb)
{
    return (size_t)RB_CAPACITY - rb_level(rb);
}

bool rb_is_ready(const ring_buffer_t *rb)
{
    return rb->rts_ready;
}

uint32_t rb_overruns(const ring_buffer_t *rb)
{
    return rb->overruns;
}
