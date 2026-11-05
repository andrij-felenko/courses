#include <stdint.h>
#include <stdbool.h>

/* Структура конфігурації подвійного буфера та стану DMA */
typedef struct {
    uint16_t *buffer_a;
    uint16_t *buffer_b;
    uint32_t buffer_size_pixels;
    volatile uint8_t active_dma_buffer; /* 0: None, 1: Buffer A, 2: Buffer B */
    volatile bool is_busy;
} display_dma_driver_t;

static display_dma_driver_t g_display_driver;

/* Запуск асинхронного передавання графічного буфера через DMA */
bool display_start_dma_transfer(uint16_t *frame_buffer, uint32_t pixel_count) {
    if (g_display_driver.is_busy) {
        return false; /* Канал DMA вже зайнятий трансляцією */
    }

    g_display_driver.is_busy = true;

    /* Переведення лінії D/C у високий рівень (Data Mode) */
    DISPLAY_DC_GPIO_PORT->BSRR = DISPLAY_DC_PIN;

    /* Вибір контролера дисплея (CS Low) */
    DISPLAY_CS_GPIO_PORT->BRR = DISPLAY_CS_PIN;

    /* Скидання кешу даних для забезпечення когерентності SRAM */
    SCB_CleanDCache_by_Addr((uint32_t *)frame_buffer, pixel_count * sizeof(uint16_t));

    /* Конфігурація регістрів DMA Engine */
    DMA1_Channel3->CCR &= ~DMA_CCR_EN; /* Вимкнення каналу для конфігурації */
    DMA1_Channel3->CPAR = (uint32_t)&(SPI1->DR); /* Адреса призначення: SPI DR */
    DMA1_Channel3->CMAR = (uint32_t)frame_buffer; /* Адреса джерела: SRAM буфер */
    DMA1_Channel3->CNDTR = pixel_count * 2;       /* Кількість байтів передачі */

    /* Увімкнення переривання TCIE та активація каналу DMA */
    DMA1_Channel3->CCR |= DMA_CCR_TCIE | DMA_CCR_DIR | DMA_CCR_MINC | DMA_CCR_EN;

    /* Дозвіл генерації DMA-запитів з боку периферичного контролера SPI */
    SPI1->CR2 |= SPI_CR2_TXDMAEN;

    return true;
}

/* Обробник переривання завершення транзакції DMA (Transfer Complete) */
void DMA1_Channel3_IRQHandler(void) {
    if (DMA1->ISR & DMA_ISR_TCIF3) {
        DMA1->IFCR = DMA_IFCR_CTCIF3; /* Очищення прапорця переривання */

        /* Деактивація DMA-запитів SPI */
        SPI1->CR2 &= ~SPI_CR2_TXDMAEN;

        /* Очікування завершення зсуву останнього байта в SPI Shift Register */
        while (SPI1->SR & SPI_SR_BSY);

        /* Деактивація вибору дисплея (CS High) */
        DISPLAY_CS_GPIO_PORT->BSRR = DISPLAY_CS_PIN;

        g_display_driver.is_busy = false;

        /* Сповіщення RTOS про завершення трансляції кадру */
        display_on_transfer_complete_callback();
    }
}
