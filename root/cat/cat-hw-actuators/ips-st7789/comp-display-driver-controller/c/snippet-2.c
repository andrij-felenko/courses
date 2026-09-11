#include <stdint.h>
#include <stdbool.h>

/* Прапорець готовності нового кадру для передачі */
static volatile bool g_frame_ready = false;
/* Прапорець активної передачі даних каналом DMA */
static volatile bool g_dma_busy = false;

/* Вказівник на буфер пікселів кадру у пам'яті мікроконтролера */
static const uint8_t *g_display_buffer = 0;
static uint32_t g_buffer_size_bytes = 0;

/**
 * Обробник апаратного переривання від лінії TE дисплея.
 * Викликається по передньому фронту сигналу вертикального гасіння (V-Blank).
 */
void Display_TE_IRQHandler(void)
{
    /* Перевіряємо, чи згенеровано новий кадр і чи вільний передавач DMA */
    if (g_frame_ready && !g_dma_busy) {
        g_frame_ready = false;
        g_dma_busy = true;

        /* Встановлюємо логічний рівень лінії вибору кристала CS в нуль */
        Display_Platform_SetCS(0);
        /* Лінія керування даними/командами D/C переводиться в режим даних (High) */
        Display_Platform_SetDC(1);

        /* Запуск асинхронної передачі буфера пікселів по SPI через DMA */
        Display_Platform_SPI_Transmit_DMA(g_display_buffer, g_buffer_size_bytes);
    }
}

/**
 * Обробник завершення передачі каналу DMA по шині SPI.
 */
void Display_DMA_Complete_IRQHandler(void)
{
    /* Піднімаємо лінію CS після завершення передачі всіх байтів кадру */
    Display_Platform_SetCS(1);
    g_dma_busy = false;
}

/**
 * Функція реєстрації нового готового кадру для відправки.
 */
void Display_Request_Frame_Update(const uint8_t *frame_data, uint32_t size)
{
    g_display_buffer = frame_data;
    g_buffer_size_bytes = size;
    /* Дозволяємо передачу при наступному стробі V-Blank */
    g_frame_ready = true;
}
