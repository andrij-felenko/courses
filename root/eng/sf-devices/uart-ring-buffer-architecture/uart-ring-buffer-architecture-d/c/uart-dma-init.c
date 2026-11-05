#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UART_DMA_BUF_SIZE 256U
#define UART_DMA_BUF_MASK (UART_DMA_BUF_SIZE - 1U)

typedef struct {
    uint8_t buffer[UART_DMA_BUF_SIZE];
    uint32_t old_head; // Попередньо оброблена позиція запису
    uint32_t tail;     // Позиція зчитування споживачем
} uart_dma_ring_t;

static uart_dma_ring_t rx_dma_ring;

// Приклад ініціалізації драйвера (псевдокод регістрів STM32/Cortex-M)
void uart_dma_init(void) {
    rx_dma_ring.old_head = 0U;
    rx_dma_ring.tail = 0U;

    // Конфігурація DMA: пам'ять у циклічному режимі, розмір буфера = UART_DMA_BUF_SIZE
    // DMA_Channel->CNDTR = UART_DMA_BUF_SIZE;
    // DMA_Channel->CMAR  = (uint32_t)rx_dma_ring.buffer;
    // DMA_Channel->CPAR  = (uint32_t)&(USART1->RDR);
    // DMA_Channel->CCR  |= DMA_CCR_CIRC | DMA_CCR_MINC | DMA_CCR_EN;

    // Увімкнення переривання IDLE в UART
    // USART1->CR1 |= USART_CR1_IDLEIE | USART_CR1_UE | USART_CR1_RE;
}

// Обробник переривання UART (викликається за подією IDLE)
void USART1_IRQHandler(void) {
    // Перевірка наявності прапорця IDLE
    // if ((USART1->ISR & USART_ISR_IDLE) != 0U) {
    //     USART1->ICR = USART_ICR_IDLECF; // Скидання прапорця IDLE

        // Зчитування поточного залишкового лічильника DMA
        // uint32_t dma_ndtr = DMA_Channel->CNDTR;
        uint32_t dma_ndtr = 200U; // Приклад: залишилося 200 байтів із 256
        uint32_t current_head = UART_DMA_BUF_SIZE - dma_ndtr;

        if (current_head != rx_dma_ring.old_head) {
            uint32_t bytes_received;
            if (current_head > rx_dma_ring.old_head) {
                bytes_received = current_head - rx_dma_ring.old_head;
            } else {
                bytes_received = (UART_DMA_BUF_SIZE - rx_dma_ring.old_head) + current_head;
            }

            rx_dma_ring.old_head = current_head; // Оновлюємо збережену позицію запису
            // Сповіщаємо фонову задачу про наявність bytes_received нових байтів
        }
    // }
}

// Зчитування байтів споживачем з DMA кольця
uint32_t uart_dma_read(uint8_t *dest, uint32_t max_len) {
    uint32_t read_bytes = 0U;
    while ((rx_dma_ring.tail != rx_dma_ring.old_head) && (read_bytes < max_len)) {
        dest[read_bytes] = rx_dma_ring.buffer[rx_dma_ring.tail];
        rx_dma_ring.tail = (rx_dma_ring.tail + 1U) & UART_DMA_BUF_MASK;
        read_bytes++;
    }
    return read_bytes;
}
