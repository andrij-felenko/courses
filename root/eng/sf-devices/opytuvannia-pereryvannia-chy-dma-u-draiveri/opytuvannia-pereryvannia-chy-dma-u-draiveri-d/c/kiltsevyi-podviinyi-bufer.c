#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DMA_BUFFER_SIZE 512  // Загальний розмір буфера (2 * N)
#define HALF_BUFFER_SIZE (DMA_BUFFER_SIZE / 2)

// Вирівнювання пам'яті по межі 32 байти для сумісності з кешем Cortex-M7
__attribute__((aligned(32))) static uint8_t g_dma_rx_buffer[DMA_BUFFER_SIZE];

typedef struct {
    volatile uint32_t CR;     // Control register
    volatile uint32_t NDTR;   // Number of data register
    volatile uint32_t PAR;    // Peripheral address register
    volatile uint32_t M0AR;   // Memory 0 address register
    volatile uint32_t FCR;    // FIFO control register
} DmaStreamHardware_t;

typedef void (*DataChunkCallback_t)(const uint8_t *data, size_t length);
static DataChunkCallback_t g_callback = NULL;

void DmaDriver_Init(DmaStreamHardware_t *dma_stream, volatile uint32_t *peripheral_dr, DataChunkCallback_t cb) {
    g_callback = cb;

    // 1. Зупинка потоку перед конфігурацією
    dma_stream->CR &= ~1u; // Clear EN bit
    while (dma_stream->CR & 1u) { /* Очікування скидання EN */ }

    // 2. Встановлення адрес периферії та буфера пам'яті
    dma_stream->PAR = (uint32_t)peripheral_dr;
    dma_stream->M0AR = (uint32_t)g_dma_rx_buffer;
    dma_stream->NDTR = DMA_BUFFER_SIZE;

    // 3. Конфігурація: MINC, CIRC, HTIE, TCIE
    uint32_t cr_config = (1u << 10) | // Memory increment (MINC)
                         (1u << 8)  | // Circular mode (CIRC)
                         (1u << 4)  | // Transfer complete interrupt enable (TCIE)
                         (1u << 3);   // Half transfer interrupt enable (HTIE)

    dma_stream->CR = cr_config;
    dma_stream->CR |= 1u; // Активація каналу DMA
}

void DMA_Stream_IRQHandler_Logic(uint32_t isr_status, volatile uint32_t *ifcr_reg) {
    #define DMA_FLAG_HTIF (1u << 4)
    #define DMA_FLAG_TCIF (1u << 5)

    // Обробляємо прапорці послідовно: навіть якщо обидва прапорці виставлені
    // через довгу критичну секцію ядра, жоден блок даних не буде втрачено
    if (isr_status & DMA_FLAG_HTIF) {
        *ifcr_reg = DMA_FLAG_HTIF; // Скидання прапорця HT
        if (g_callback) {
            g_callback(&g_dma_rx_buffer[0], HALF_BUFFER_SIZE);
        }
    }

    if (isr_status & DMA_FLAG_TCIF) {
        *ifcr_reg = DMA_FLAG_TCIF; // Скидання прапорця TC
        if (g_callback) {
            g_callback(&g_dma_rx_buffer[HALF_BUFFER_SIZE], HALF_BUFFER_SIZE);
        }
    }
}
