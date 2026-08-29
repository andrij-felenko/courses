/* Кільце SPSC для мосту «ISR → фонове завдання».
 *
 * Один постачальник — обробник переривання — рухає ЛИШЕ head.
 * Один споживач — фонове завдання — рухає ЛИШЕ tail.
 * Жоден покажчик не змінюється двома контекстами, тож ні вимикати
 * переривання, ні брати замок не треба.
 *
 * Заголовок навмисно header-only й увесь на static inline: виклик із ISR
 * не має коштувати переходу через межу модуля.
 */
#ifndef SPSC_RING_H
#define SPSC_RING_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define RING_BUFFER_SIZE 256u
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1u) /* 0xFF: індекс сам себе загортає */

#if (RING_BUFFER_SIZE & RING_BUFFER_MASK) != 0u
#error "RING_BUFFER_SIZE мусить бути степенем двійки: маска заміняє ділення"
#endif

/* Бар'єр пам'яті. На Cortex-M потрібен справжній DMB: ядро має право
 * переставити запис байта в масив і запис нового head місцями, і споживач
 * побачить індекс раніше за дані. На AVR ядро однопотокове й in-order,
 * тож досить бар'єра для компілятора. */
#if defined(__ARM_ARCH) || defined(__ARM_ARCH_7EM__)
#define RING_BARRIER() __asm volatile("dmb 0xF" ::: "memory")
#else
#define RING_BARRIER() __asm volatile("" ::: "memory")
#endif

/* Індекси навмисно ОДНОБАЙТОВІ, а розмір кільця дорівнює 256.
 * Кожен індекс пише один контекст, але ЧИТАЄ його інший — і читання мусить
 * бути неподільним. Однобайтове звернення неподільне і на Cortex-M (LDRB),
 * і на восьмибітному AVR; 32-бітний лічильник на AVR читався б чотирма
 * інструкціями й рвався б посеред читання. */
typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint8_t head; /* пише лише постачальник (ISR) */
    volatile uint8_t tail; /* пише лише споживач (завдання) */
} spsc_ring_buffer_t;

static inline void ring_buffer_init(spsc_ring_buffer_t *rb)
{
    rb->head = 0u;
    rb->tail = 0u;
}

/* Верхня половина. Повертає false, коли кільце повне — тоді байт
 * втрачено СВІДОМО, і це фіксується лічильником, а не зависанням. */
static inline bool ring_buffer_push_isr(spsc_ring_buffer_t *rb, uint8_t byte)
{
    const uint8_t head = rb->head;
    const uint8_t next_head = (uint8_t)((head + 1u) & RING_BUFFER_MASK);

    if (next_head == rb->tail) {
        return false; /* повне: наздогнали хвіст */
    }

    rb->buffer[head] = byte;
    RING_BARRIER(); /* дані лягли ДО того, як індекс став видимим */
    rb->head = next_head;
    return true;
}

/* Нижня половина. Повертає false, коли читати нічого. */
static inline bool ring_buffer_pop_main(spsc_ring_buffer_t *rb, uint8_t *out)
{
    const uint8_t tail = rb->tail;

    if (tail == rb->head) {
        return false; /* порожнє */
    }

    *out = rb->buffer[tail];
    RING_BARRIER(); /* байт прочитано ДО звільнення комірки */
    rb->tail = (uint8_t)((tail + 1u) & RING_BUFFER_MASK);
    return true;
}

static inline uint8_t ring_buffer_count(const spsc_ring_buffer_t *rb)
{
    return (uint8_t)(rb->head - rb->tail);
}

#endif /* SPSC_RING_H */
