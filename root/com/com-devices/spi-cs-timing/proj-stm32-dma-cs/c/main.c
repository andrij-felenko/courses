#include "stm32f4xx_ll_spi.h"
#include "stm32f4xx_ll_dma.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"
#include <stdint.h>
#include <stdbool.h>

/* Конфігурація порту та виводу лінії CS */
#define SPI_CS_PORT GPIOA
#define SPI_CS_PIN  LL_GPIO_PIN_4

/* Функція захисної мікропаузи для витримки t_CSS та t_CSH */
static inline void spi_guard_delay(void) {
    __NOP(); __NOP(); __NOP(); __NOP();
    __NOP(); __NOP(); __NOP(); __NOP();
}

/* Ініціалізація виводу CS у режимі швидкісного двотактного виходу */
void spi_cs_init(void) {
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    
    LL_GPIO_SetPinMode(SPI_CS_PORT, SPI_CS_PIN, LL_GPIO_MODE_OUTPUT);
    LL_GPIO_SetPinOutputType(SPI_CS_PORT, SPI_CS_PIN, LL_GPIO_OUTPUT_PUSHPULL);
    LL_GPIO_SetPinSpeed(SPI_CS_PORT, SPI_CS_PIN, LL_GPIO_SPEED_FREQ_VERY_HIGH);
    LL_GPIO_SetPinPull(SPI_CS_PORT, SPI_CS_PIN, LL_GPIO_PULL_UP);
    
    /* За замовчуванням лінія CS деактивована (високий рівень) */
    LL_GPIO_SetOutputPin(SPI_CS_PORT, SPI_CS_PIN);
}

/* Активація вибору кристала з гарантованою витримкою t_CSS */
void spi_cs_assert(void) {
    LL_GPIO_ResetOutputPin(SPI_CS_PORT, SPI_CS_PIN);
    spi_guard_delay(); /* Гарантуємо t_CSS перед першим тактом SCLK */
}

/* Безпечна деактивація CS з повною перевіркою зсувного регістра */
void spi_cs_deassert(SPI_TypeDef *SPIx) {
    /* 1. Очікуємо повного спорожнення вхідного буфера даних */
    while (!LL_SPI_IsActiveFlag_TXE(SPIx)) {
        /* Чекаємо готовності буфера TXDR */
    }

    /* 2. КРИТИЧНИЙ ЕТАП: чекаємо завершення фізичного тактування в лінії */
    while (LL_SPI_IsActiveFlag_BSY(SPIx)) {
        /* Прапорець BSY активний, поки зсувний регістр жене біти в MOSI */
    }

    /* 3. Витримуємо час утримання t_CSH після останнього спаду SCLK */
    spi_guard_delay();

    /* 4. Переводимо лінію CS у високий стан */
    LL_GPIO_SetOutputPin(SPI_CS_PORT, SPI_CS_PIN);
    
    /* 5. Витримуємо час неактивності t_CS_HIGH перед наступною операцією */
    spi_guard_delay();
}

/* Блокуюча функція передачі блоку пам'яті через DMA з контролем CS */
bool spi_dma_transmit_sync(SPI_TypeDef *SPIx, DMA_TypeDef *DMAx, uint32_t Stream,
                           const uint8_t *tx_buffer, uint32_t length) {
    if (tx_buffer == NULL || length == 0) {
        return false;
    }

    /* Крок 1: Опускаємо CS */
    spi_cs_assert();

    /* Крок 2: Налаштовуємо параметри DMA */
    LL_DMA_DisableStream(DMAx, Stream);
    LL_DMA_SetMemoryAddress(DMAx, Stream, (uint32_t)tx_buffer);
    LL_DMA_SetDataLength(DMAx, Stream, length);
    LL_DMA_ClearFlag_TC4(DMAx);
    LL_DMA_ClearFlag_TE4(DMAx);

    /* Крок 3: Запускаємо передачу */
    LL_SPI_EnableDMAReq_TX(SPIx);
    LL_DMA_EnableStream(DMAx, Stream);
    LL_SPI_Enable(SPIx);

    /* Крок 4: Очікуємо вивантаження пам'яті контролером DMA */
    while (!LL_DMA_IsActiveFlag_TC4(DMAx)) {
        if (LL_DMA_IsActiveFlag_TE4(DMAx)) {
            /* Обробка апаратної помилки шини DMA */
            LL_DMA_DisableStream(DMAx, Stream);
            LL_SPI_DisableDMAReq_TX(SPIx);
            spi_cs_deassert(SPIx);
            return false;
        }
    }

    /* Крок 5: Зупиняємо запити DMA */
    LL_DMA_DisableStream(DMAx, Stream);
    LL_SPI_DisableDMAReq_TX(SPIx);

    /* Крок 6: Безпечно знімаємо CS після звільнення зсувного регістра */
    spi_cs_deassert(SPIx);
    return true;
}
