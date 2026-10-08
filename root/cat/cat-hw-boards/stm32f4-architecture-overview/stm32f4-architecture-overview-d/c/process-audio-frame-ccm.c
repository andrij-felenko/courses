// C: Розподіл пам'яті між CCM SRAM (критичні дані ядра) та основною SRAM1 (буфери DMA)
#include "stm32f4xx.h"
#include <arm_math.h>

#define AUDIO_BLOCK_SIZE 256

// Буфер DMA розташований у стандартній SRAM1 (доступний для DMA2)
uint16_t dma_adc_buffer[AUDIO_BLOCK_SIZE] __attribute__((section(".sram1_data")));

// Буфер коефіцієнтів фільтра та стан алгоритму розташовані в CCM SRAM (0 wait-state, доступ лише ядру)
float32_t dsp_filter_state[AUDIO_BLOCK_SIZE] __attribute__((section(".ccmram")));
float32_t dsp_coefficients[5] __attribute__((section(".ccmram"))) = {0.1f, 0.2f, 0.4f, 0.2f, 0.1f};

void process_audio_frame_ccm(void) {
    // Ядро зчитує дані з dma_adc_buffer (SRAM1) та виконує обчислення в CCM SRAM без затримок шини
    for (int i = 0; i < AUDIO_BLOCK_SIZE; i++) {
        dsp_filter_state[i] = ((float32_t)dma_adc_buffer[i] / 4095.0f) * dsp_coefficients[2];
    }
}
