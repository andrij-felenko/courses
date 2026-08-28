#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define UART_RING_BUF_SIZE 128u
#define UART_RING_BUF_MASK (UART_RING_BUF_SIZE - 1u)

/* Перевірка на етапі компіляції: розмір буфера мусить бути степенем двійки */
typedef char static_assert_ring_power_of_two[(UART_RING_BUF_SIZE & UART_RING_BUF_MASK) == 0 ? 1 : -1];

typedef struct {
    uint8_t storage[UART_RING_BUF_SIZE];
    volatile uint32_t head; /* Індекс запису (оновлюється в ISR) */
    volatile uint32_t tail; /* Індекс читання (оновлюється в main) */
} uart_ring_buffer_t;

void ring_buf_init(uart_ring_buffer_t *rb) {
    if (rb != NULL) {
        rb->head = 0u;
        rb->tail = 0u;
    }
}

/* Викликається виключно з контексту переривання UART RX ISR */
bool ring_buf_put_from_isr(uart_ring_buffer_t *rb, uint8_t byte) {
    if (rb == NULL) {
        return false;
    }
    uint32_t current_head = rb->head;
    uint32_t next_head = (current_head + 1u) & UART_RING_BUF_MASK;

    /* Якщо наступний індекс голови досяг хвоста — буфер переповнено */
    if (next_head == rb->tail) {
        return false;
    }

    rb->storage[current_head] = byte;
    rb->head = next_head; /* Атомарне оновлення 32-бітного слова на ARM Cortex-M */
    return true;
}

/* Викликається з основного фонового циклу */
bool ring_buf_get(uart_ring_buffer_t *rb, uint8_t *out_byte) {
    if ((rb == NULL) || (out_byte == NULL)) {
        return false;
    }
    uint32_t current_tail = rb->tail;

    /* Якщо хвіст наздогнав голову — буфер порожній */
    if (current_tail == rb->head) {
        return false;
    }

    *out_byte = rb->storage[current_tail];
    rb->tail = (current_tail + 1u) & UART_RING_BUF_MASK;
    return true;
}
