#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define DVP_BUFFER_SIZE (32 * 1024) // Розмір половини кільцевого буфера (32 КБ)

uint8_t g_dvp_ping_pong_buffer[DVP_BUFFER_SIZE * 2];
volatile bool g_frame_ready = false;
volatile bool g_frame_busy = false;
volatile uint32_t g_captured_bytes = 0;

// Обробник переривання DMA (Half-Transfer та Transfer-Complete)
void DMA2_Stream1_IRQHandler(void) {
    // Перевірка переривання половини передачі (Buffer 0 заповнено)
    if (__HAL_DMA_GET_FLAG(&hdma_dcmi, DMA_FLAG_HTIF1_5)) {
        __HAL_DMA_CLEAR_FLAG(&hdma_dcmi, DMA_FLAG_HTIF1_5);
        if (!g_frame_busy) {
            // Обробка Buffer 0 (перші DVP_BUFFER_SIZE байтів)
            process_jpeg_chunk(&g_dvp_ping_pong_buffer[0], DVP_BUFFER_SIZE);
        }
    }
    // Перевірка переривання повного завершення (Buffer 1 заповнено)
    if (__HAL_DMA_GET_FLAG(&hdma_dcmi, DMA_FLAG_TCIF1_5)) {
        __HAL_DMA_CLEAR_FLAG(&hdma_dcmi, DMA_FLAG_TCIF1_5);
        if (!g_frame_busy) {
            // Обробка Buffer 1 (другі DVP_BUFFER_SIZE байтів)
            process_jpeg_chunk(&g_dvp_ping_pong_buffer[DVP_BUFFER_SIZE], DVP_BUFFER_SIZE);
        }
    }
}

// Обробник переривання VSYNC (кадр повністю сформовано сенсором)
void EXTI9_5_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(VSYNC_PIN)) {
        __HAL_GPIO_EXTI_CLEAR_IT(VSYNC_PIN);
        
        if (g_frame_busy) {
            // Процесор ще обробляє попередній кадр: пропускаємо новий
            HAL_DCMI_Stop(&hdcmi);
        } else {
            // Фіксуємо розмір кадру та сигналізуємо готовність
            g_captured_bytes = DVP_BUFFER_SIZE * 2 - __HAL_DMA_GET_COUNTER(&hdma_dcmi);
            g_frame_ready = true;
        }
    }
}
