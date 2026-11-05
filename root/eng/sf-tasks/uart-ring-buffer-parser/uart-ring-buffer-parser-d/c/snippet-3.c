#include <stdint.h>
#include <stdbool.h>

#define RING_BUFFER_SIZE 128U
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1U)

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} uart_ring_buffer_t;

/* Обробник переривання UART по побайтовому прийому (ISR) */
void USART1_IRQHandler_ISR(uart_ring_buffer_t *ring, uint8_t rx_byte) {
    uint32_t next_head = (ring->head + 1U) & RING_BUFFER_MASK;
    if (next_head != ring->tail) {
        ring->buffer[ring->head] = rx_byte;
        __asm__ volatile("" ::: "memory"); // Бар'єр пам'яті
        ring->head = next_head;
    }
    /* Якщо next_head == tail, буфер переповнений, байт відкидається */
}

/* Оновлення head при використанні Circular DMA за лічильником NDTR */
void UART_DMA_Sync_Head(uart_ring_buffer_t *ring, uint32_t dma_ndtr) {
    /* dma_ndtr зменшується від RING_BUFFER_SIZE до 1 */
    uint32_t current_dma_pos = (RING_BUFFER_SIZE - dma_ndtr) & RING_BUFFER_MASK;
    ring->head = current_dma_pos;
}
