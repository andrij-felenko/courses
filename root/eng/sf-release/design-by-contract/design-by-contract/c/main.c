#include <assert.h>
#include <stdint.h>
#include <stdbool.h>

#define RB_CAP 64

typedef struct {
    uint8_t  buf[RB_CAP];
    uint16_t head;     // куди писати
    uint16_t tail;     // звідки читати
    uint16_t count;    // скільки зараз у буфері
} ring_t;

// ІНВАРІАНТ модуля: усе, що мусить бути істинним до і після кожної операції.
// Виносимо в окрему функцію, щоб assert'и не дублювати в кожному методі.
static inline bool rb_invariant(const ring_t *rb) {
    return rb->head  < RB_CAP &&
           rb->tail  < RB_CAP &&
           rb->count <= RB_CAP &&
           // head завжди на count позицій попереду tail (по колу) — одна
           // рівність, що тримається і для порожнього, і для повного буфера
           rb->head == (rb->tail + rb->count) % RB_CAP;
}

esp_err_t rb_push(ring_t *rb, uint8_t byte) {
    // ПЕРЕДУМОВА — борг викликача: вказівник справний, структура ціла.
    assert(rb != NULL);
    assert(rb_invariant(rb));

    // ОЧІКУВАНА ситуація (не порушення контракту!): буфер просто повний.
    // Це нормальний стан роботи, тож код повернення, а не assert.
    if (rb->count == RB_CAP) {
        return ESP_ERR_NO_MEM;
    }

    rb->buf[rb->head] = byte;
    rb->head = (rb->head + 1) % RB_CAP;   // тут інваріант на мить «в дорозі»
    rb->count++;                          // ...і знову відновлений

    // ПОСТУМОВА — борг функції: після успіху в буфері рівно на один більше,
    // і структура знову в дозволеному стані.
    assert(rb->count >= 1);
    assert(rb_invariant(rb));
    return ESP_OK;
}
