#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UART_RX_RING_SIZE    1024U

typedef struct {
    uint8_t  buffer[UART_RX_RING_SIZE];
    uint16_t tail;
} uart_dma_ring_t;

/* Отримання поточного положення апаратного запису DMA (наприклад, для STM32) */
static inline uint16_t get_dma_head(uint16_t dma_cndtr_val) {
    return (uint16_t)(UART_RX_RING_SIZE - dma_cndtr_val);
}

/* Вичитка повного рядка, завершеного \r або \n, без копіювання */
bool uart_ring_get_line(uart_dma_ring_t *ring, uint16_t dma_cndtr_val, 
                        char *out_line, size_t max_out_len) {
    uint16_t head = get_dma_head(dma_cndtr_val);
    uint16_t tail = ring->tail;
    
    if (head == tail) {
        return false; /* Немає нових даних */
    }

    /* Пошук символу кінця рядка \n */
    uint16_t scan_idx = tail;
    bool line_found = false;
    size_t line_len = 0;

    while (scan_idx != head) {
        uint8_t b = ring->buffer[scan_idx];
        if (b == '\n') {
            line_found = true;
            break;
        }
        scan_idx = (uint16_t)((scan_idx + 1U) % UART_RX_RING_SIZE);
        line_len++;
        if (line_len >= max_out_len - 1U) {
            /* Захист від переповнення вихідного буфера: скидаємо пошкоджений рядок */
            ring->tail = scan_idx;
            return false;
        }
    }

    if (!line_found) {
        return false; /* Рядок ще не надійшов повністю */
    }

    /* Копіюємо сформований рядок у вихідний буфер, відкидаючи \r і \n */
    size_t out_idx = 0;
    while (ring->tail != scan_idx) {
        uint8_t b = ring->buffer[ring->tail];
        if (b != '\r' && b != '\n') {
            if (out_idx < max_out_len - 1U) {
                out_line[out_idx++] = (char)b;
            }
        }
        ring->tail = (uint16_t)((ring->tail + 1U) % UART_RX_RING_SIZE);
    }
    
    /* Пропускаємо сам символ '\n' */
    ring->tail = (uint16_t)((ring->tail + 1U) % UART_RX_RING_SIZE);
    out_line[out_idx] = '\0';

    return (out_idx > 0); /* Повертаємо true, якщо рядок не порожній */
}
