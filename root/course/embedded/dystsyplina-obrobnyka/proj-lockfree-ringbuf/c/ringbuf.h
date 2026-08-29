/* SPSC кільцевий буфер без блокувань: один постачальник (обробник переривання)
   і один споживач (головний цикл). Жодних м'ютексів, жодного вимкнення
   переривань, жодної купи — масив лежить у BSS разом зі структурою. */

#ifndef RINGBUF_H
#define RINGBUF_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Ємність мусить бути степенем двійки: закільцьовування робиться маскою,
   а не діленням (UDIV на Cortex-M коштує десятки тактів). Один слот завжди
   лишається порожнім, бо стан head == tail зарезервовано під «порожньо»,
   тож корисна місткість — RB_CAPACITY - 1 байт. */
#define RB_CAPACITY 128u
#define RB_MASK     (RB_CAPACITY - 1u)

#if (RB_CAPACITY & RB_MASK) != 0u
#error "RB_CAPACITY має бути степенем двійки"
#endif

/* Бар'єр пам'яті. На ARMv7-M/ARMv8-M це інструкція DMB: вона не дає ані
   компіляторові, ані буферу запису шини переставити публікацію індексу
   поперед запису самих даних. На хості, де ми ганяємо демонстрацію,
   ту саму роль виконує повний бар'єр компілятора й процесора. */
#if defined(__ARM_ARCH) && (__ARM_ARCH >= 7)
#define rb_barrier() __asm volatile("dmb 0xF" ::: "memory")
#elif defined(__GNUC__) || defined(__clang__)
#define rb_barrier() __atomic_thread_fence(__ATOMIC_SEQ_CST)
#else
#include <stdatomic.h>
#define rb_barrier() atomic_thread_fence(memory_order_seq_cst)
#endif

/* Довжина лінії кешу: 32 байти на Cortex-M7, 64 на Cortex-A та x86.
   Беремо більше — вирівнювання із запасом нічого не ламає. */
#ifndef RB_CACHE_LINE
#define RB_CACHE_LINE 64u
#endif

typedef struct {
    _Alignas(RB_CACHE_LINE) uint8_t storage[RB_CAPACITY];

    /* Лінія постачальника. head і лічильник втрат пише ЛИШЕ обробник
       переривання; споживач їх лише читає. */
    _Alignas(RB_CACHE_LINE) volatile uint32_t head;
    volatile uint32_t dropped;

    /* Лінія споживача. tail пише ЛИШЕ головний цикл. Окрема лінія кешу
       прибирає хибне розділення (false sharing) на дво'ядерних МК. */
    _Alignas(RB_CACHE_LINE) volatile uint32_t tail;
} rb_t;

void rb_init(rb_t *rb);

/* --- сторона обробника переривання --- */

/* Кладе байт. false означає переповнення: байт втрачено, лічильник зріс.
   Час виконання фіксований — ні циклів очікування, ні викликів. */
bool rb_push_isr(rb_t *rb, uint8_t byte);

/* Те саме для UART з апаратним FIFO: кілька байтів за одне переривання,
   один бар'єр на всю пачку. Повертає, скільки байтів прийнято. */
size_t rb_push_isr_burst(rb_t *rb, const uint8_t *data, size_t len);

uint32_t rb_dropped(const rb_t *rb);

/* --- сторона головного циклу --- */

bool rb_pop(rb_t *rb, uint8_t *out);
size_t rb_pop_burst(rb_t *rb, uint8_t *out, size_t max);

/* Викинути найстаріші байти, коли важливі лише найсвіжіші дані. Робить це
   СПОЖИВАЧ, бо tail належить йому; обробник переривання при цьому просто
   бачить більше вільного місця. Повертає, скільки викинуто. */
size_t rb_discard_oldest(rb_t *rb, size_t count);

size_t rb_available(const rb_t *rb);

static inline size_t rb_capacity(void) { return RB_CAPACITY - 1u; }

#endif /* RINGBUF_H */
