/* services/ring_buffer.h — кільцевий буфер елементів довільного розміру.
 * Служба на 100% переносна: жодного включення з hal/ чи bsp/, жодного
 * malloc. Пам'ять дає викликач, тому той самий код працює і на Cortex-M0
 * з двома кілобайтами RAM, і в модульному тесті на x86-64.
 *
 * Сам буфер не робить нічого для взаємного виключення: він не знає, чи
 * штовхає в нього переривання. Синхронізацію додає той, хто ним володіє
 * (див. services/event_queue.c). */
#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdbool.h>
#include <stddef.h>

typedef struct {
    unsigned char *storage;
    size_t         elem_size;
    size_t         capacity;
    size_t         head;   /* куди писати */
    size_t         tail;   /* звідки читати */
    size_t         count;
} ring_buffer_t;

/* storage мусить бути не менший за elem_size * capacity. */
bool ring_buffer_init(ring_buffer_t *rb, void *storage,
                      size_t elem_size, size_t capacity);

void   ring_buffer_reset(ring_buffer_t *rb);
size_t ring_buffer_count(const ring_buffer_t *rb);
size_t ring_buffer_free(const ring_buffer_t *rb);
bool   ring_buffer_is_empty(const ring_buffer_t *rb);
bool   ring_buffer_is_full(const ring_buffer_t *rb);

/* Кладе копію елемента. false — буфер повний, елемент НЕ втрачено мовчки:
 * викликач вирішує, рахувати це втратою чи відкинути найстаріший запис. */
bool ring_buffer_push(ring_buffer_t *rb, const void *elem);

/* Кладе, витиснувши найстаріший елемент, коли місця немає.
 * Повертає true, якщо довелося щось викинути. */
bool ring_buffer_push_overwrite(ring_buffer_t *rb, const void *elem);

bool ring_buffer_pop(ring_buffer_t *rb, void *out_elem);
bool ring_buffer_peek(const ring_buffer_t *rb, void *out_elem);

#endif /* RING_BUFFER_H */
