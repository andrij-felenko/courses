#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

// Фізичні часові параметри зовнішнього сенсора з документації
#define SENSOR_RESET_HOLD_US     15000U  // 15 мс утримання апаратного скидання
#define SENSOR_BOOT_READY_US     25000U  // 25 мс очікування внутрішнього завантаження

static void delay_us(uint32_t us) {
    // Відлік мікросекунд на базі лічильника циклів DWT ядра Cortex-M
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = us * (SystemCoreClock / 1000000U);
    while ((DWT->CYCCNT - start) < ticks) {
        __NOP();
    }
}

typedef enum {
    INIT_OK = 0,
    INIT_ERR_TIMEOUT,
    INIT_ERR_CHIP_ID
} init_status_t;

init_status_t sensor_subsystem_init(uint8_t *rx_dma_buf, uint16_t buf_len) {
    // 1. Увімкнення лічильника DWT для точних мікросекундних пауз
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    // 2. Увімкнення тактування шин RCC для GPIOA, GPIOC, SPI1 та DMA2
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOCEN | RCC_AHB1ENR_DMA2EN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    (void)RCC->APB2ENR; // Фіктивне читання для стабілізації шинного мосту

    // 3. Безпечна конфігурація виводів: спершу засувки, потім режими
    // PC4: апаратне скидання сенсора (nRST, active LOW) -> спочатку притискаємо до LOW
    GPIOC->BSRR = GPIO_BSRR_BR4;
    GPIOC->MODER &= ~GPIO_MODER_MODER4_Msk;
    GPIOC->MODER |= (1U << GPIO_MODER_MODER4_Pos); // Вихід

    // PA4: Chip Select (nCS, active LOW) -> спочатку виставляємо HIGH!
    GPIOA->BSRR = GPIO_BSRR_BS4;
    GPIOA->MODER &= ~GPIO_MODER_MODER4_Msk;
    GPIOA->MODER |= (1U << GPIO_MODER_MODER4_Pos); // Вихід

    // PA5 (SCK), PA6 (MISO), PA7 (MOSI): альтернативна функція AF5 (SPI1)
    GPIOA->MODER &= ~(GPIO_MODER_MODER5_Msk | GPIO_MODER_MODER6_Msk | GPIO_MODER_MODER7_Msk);
    GPIOA->MODER |= (2U << GPIO_MODER_MODER5_Pos) | 
                    (2U << GPIO_MODER_MODER6_Pos) | 
                    (2U << GPIO_MODER_MODER7_Pos);
    GPIOA->AFR[0] |= (5U << GPIO_AFRL_AFSEL5_Pos) | 
                     (5U << GPIO_AFRL_AFSEL6_Pos) | 
                     (5U << GPIO_AFRL_AFSEL7_Pos);
    GPIOA->OSPEEDR |= (3U << GPIO_OSPEEDR_OSPEED5_Pos) | 
                      (3U << GPIO_OSPEEDR_OSPEED7_Pos); // High speed

    // 4. Витримка апаратного скидання зовнішнього чипа
    delay_us(SENSOR_RESET_HOLD_US);
    GPIOC->BSRR = GPIO_BSRR_BS4; // Зняття Reset (nRST = HIGH)
    delay_us(SENSOR_BOOT_READY_US); // Очікування внутрішньої готовності чипа

    // 5. Конфігурація модуля DMA (DMA2 Stream 0 Channel 3 = SPI1_RX)
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA2_Stream0->CR & DMA_SxCR_EN) { /* Чекаємо вимкнення */ }

    DMA2->LIFCR = DMA_LIFCR_CTCIF0 | DMA_LIFCR_CTEIF0 | DMA_LIFCR_CDMEIF0 | DMA_LIFCR_CFEIF0;
    DMA2_Stream0->PAR = (uint32_t)&(SPI1->DR);
    DMA2_Stream0->M0AR = (uint32_t)rx_dma_buf;
    DMA2_Stream0->NDTR = buf_len;
    DMA2_Stream0->CR = (3U << DMA_SxCR_CHSEL_Pos) | // Канал 3
                       DMA_SxCR_MINC |              // Інкремент пам'яті
                       (1U << DMA_SxCR_PL_Pos) |    // Середній пріоритет
                       DMA_SxCR_TCIE;               // Переривання по завершенню

    // 6. Налаштування регістрів SPI1 (Master Mode, Baud = F_PCLK / 8, CPOL=0, CPHA=0)
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (2U << SPI_CR1_BR_Pos);
    (void)SPI1->SR; // Очищення можливих прапорців читанням
    (void)SPI1->DR;

    // 7. Конфігурація NVIC
    NVIC_SetPriority(DMA2_Stream0_IRQn, 5);
    NVIC_ClearPendingIRQ(DMA2_Stream0_IRQn);
    NVIC_EnableIRQ(DMA2_Stream0_IRQn);

    // 8. Увімкнення DMA-потоку ПЕРЕД увімкненням периферії
    DMA2_Stream0->CR |= DMA_SxCR_EN;

    // 9. Дозвіл DMA-запитів у SPI та фінальна активація інтерфейсу
    SPI1->CR2 |= SPI_CR2_RXDMAEN;
    SPI1->CR1 |= SPI_CR1_SPE;

    return INIT_OK;
}
