/* c */
#include <stdint.h>
#include <stdbool.h>

#define LOOP_BUF_SIZE 128

typedef enum {
    LOOP_OK = 0,
    LOOP_ERR_EMPTY,
    LOOP_ERR_BREAK_FAULT // Обрив струмової петлі (0 мА)
} loop_err_t;

typedef struct {
    uint8_t buf[LOOP_BUF_SIZE];
    uint16_t head;
    uint16_t tail;
    bool line_fault;
} current_loop_rx_t;

// Обробник переривання UART RX
void current_loop_isr(current_loop_rx_t *rx, uint8_t byte, bool break_detected) {
    if (break_detected) {
        rx->line_fault = true; // Аварія: струм припинився понад 12 бітів
        return;
    }
    uint16_t next = (rx->head + 1) % LOOP_BUF_SIZE;
    if (next != rx->tail) {
        rx->buf[rx->head] = byte;
        rx->head = next;
    }
}

loop_err_t current_loop_pop(current_loop_rx_t *rx, uint8_t *byte) {
    if (rx->line_fault) return LOOP_ERR_BREAK_FAULT;
    if (rx->head == rx->tail) return LOOP_ERR_EMPTY;
    *byte = rx->buf[rx->tail];
    rx->tail = (rx->tail + 1) % LOOP_BUF_SIZE;
    return LOOP_OK;
}
