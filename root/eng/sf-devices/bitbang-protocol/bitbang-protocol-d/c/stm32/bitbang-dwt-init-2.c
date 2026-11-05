#include "stm32f4xx.h"
#include <stdint.h>

// Оголошення структури конфігурації Bit-bang SPI
typedef struct {
    GPIO_TypeDef* port_sck;
    uint16_t      pin_sck;
    GPIO_TypeDef* port_mosi;
    uint16_t      pin_mosi;
    GPIO_TypeDef* port_miso;
    uint16_t      pin_miso;
} bitbang_spi_config_t;

// Ініціалізація тактів DWT для вимірювання затримок
static inline void bitbang_dwt_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// Функція передачі та прийому байта з кешуванням регістрових масок і розгортанням циклу
uint8_t bitbang_spi_transfer_fast(const bitbang_spi_config_t* cfg, uint8_t tx_data) {
    // Попередній розрахунок атомарних масок BSRR для даних
    uint32_t mosi_high = (uint32_t)cfg->pin_mosi;
    uint32_t mosi_low  = (uint32_t)cfg->pin_mosi << 16;
    
    // Атомарні маски BSRR для стробу годинника SCL/SCK
    uint32_t sck_high  = (uint32_t)cfg->pin_sck;
    uint32_t sck_low   = (uint32_t)cfg->pin_sck << 16;

    // Кешування масок для кожного біта у масив для досягнення максимальної швидкості
    uint32_t tx_masks[8];
    for (int i = 0; i < 8; i++) {
        tx_masks[i] = (tx_data & (1U << (7 - i))) ? mosi_high : mosi_low;
    }

    uint8_t rx_data = 0;

    // Захист критичної секції від переривань
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    // Розгорнутий цикл обробки 8 бітів (без інструкцій умовного переходу)
    #define BIT_STEP(n) \
        cfg->port_mosi->BSRR = tx_masks[n]; \
        __NOP(); \
        cfg->port_sck->BSRR  = sck_high; \
        __DSB(); \
        if (cfg->port_miso->IDR & cfg->pin_miso) { rx_data |= (1U << (7 - n)); } \
        cfg->port_sck->BSRR  = sck_low; \
        __NOP();

    BIT_STEP(0);
    BIT_STEP(1);
    BIT_STEP(2);
    BIT_STEP(3);
    BIT_STEP(4);
    BIT_STEP(5);
    BIT_STEP(6);
    BIT_STEP(7);

    #undef BIT_STEP

    // Відновлення стану переривань
    if (!primask) {
        __enable_irq();
    }

    return rx_data;
}
