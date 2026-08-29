/* Кільцевий буфер приймача з гістерезисними порогами й керуванням лінією /RTS.
 *
 * Розподіл ролей жорсткий: head пише ЛИШЕ переривання прийому, tail — ЛИШЕ
 * споживач. Спільного лічильника count немає навмисно: саме він і був би тим
 * місцем, де ISR і фонове завдання затирають одне одному запис. */
#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Місткість мусить бути степенем двійки: індекси зростають вільно, а в масив
 * адресуємо маскою. Так не треба ділити з остачею й не треба тримати окремий
 * прапорець «повний/порожній». */
#define RB_CAPACITY 256u
#define RB_MASK (RB_CAPACITY - 1u)

/* 192 байти: далі піднімаємо /RTS у Busy. Решта 64 — запас на байти в польоті:
 * зсувний регістр передавача, кабель і затримка реакції на переривання. */
#define RB_HIGH_WATERMARK (RB_CAPACITY * 3u / 4u)
/* 64 байти: лише тут опускаємо /RTS назад у Ready. Смуга гістерезису — 128 байтів. */
#define RB_LOW_WATERMARK (RB_CAPACITY / 4u)

/* Драйвер лінії: true — дозвіл передавати (/RTS = 0 В), false — пауза (/RTS = 3.3 В). */
typedef void (*rb_rts_fn)(bool ready);

typedef struct {
    uint8_t storage[RB_CAPACITY];
    volatile uint32_t head; /* пише лише ISR */
    volatile uint32_t tail; /* пише лише споживач */
    volatile bool rts_ready; /* дзеркало стану лінії */
    volatile uint32_t overruns; /* байти, що не влізли: буфер був повний */
    rb_rts_fn set_rts;
} ring_buffer_t;

void rb_init(ring_buffer_t *rb, rb_rts_fn set_rts);

/* Виклик із ISR прийому UART або з half-transfer колбека DMA. */
bool rb_push_from_isr(ring_buffer_t *rb, uint8_t byte);

/* Виклик із основного циклу або завдання RTOS. */
bool rb_pop(ring_buffer_t *rb, uint8_t *out_byte);

/* Вигрібання пачкою: один зсув tail і одна перевірка порога на всю пачку. */
size_t rb_pop_bulk(ring_buffer_t *rb, uint8_t *dst, size_t max_bytes);

size_t rb_level(const ring_buffer_t *rb);
size_t rb_free_space(const ring_buffer_t *rb);
bool rb_is_ready(const ring_buffer_t *rb);
uint32_t rb_overruns(const ring_buffer_t *rb);

#endif /* RING_BUFFER_H */
