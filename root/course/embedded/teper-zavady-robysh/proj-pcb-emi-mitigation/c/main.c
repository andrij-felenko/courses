#include <stdint.h>
#include "stm32f4xx.h"

/* Рівні швидкості вихідного каскаду GPIO */
typedef enum {
    GPIO_SPEED_LOW_2MHZ      = 0x00U, /* Фронти ~15-25 нс: UART, LED, реле, повільний I2C */
    GPIO_SPEED_MEDIUM_25MHZ  = 0x01U, /* Фронти ~4-6 нс: SPI до 10 МГц, ШІМ до 100 кГц */
    GPIO_SPEED_FAST_50MHZ    = 0x02U, /* Фронти ~2-3 нс: швидкий SPI, дисплеї */
    GPIO_SPEED_HIGH_100MHZ   = 0x03U  /* Фронти <1.2 нс: тільки SDIO, FMC, паралельні шини */
} gpio_slew_rate_t;

typedef struct {
    GPIO_TypeDef     *port;
    uint32_t          pin_mask;
    gpio_slew_rate_t  slew_rate;
} pin_emi_config_t;

void gpio_configure_slew_rate(const pin_emi_config_t *configs, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        GPIO_TypeDef *port = configs[i].port;
        uint32_t mask = configs[i].pin_mask;
        uint32_t speed = (uint32_t)configs[i].slew_rate;

        for (uint32_t pin = 0; pin < 16; ++pin) {
            if (mask & (1U << pin)) {
                /* Очищення двох бітів конфігурації швидкості в OSPEEDR */
                port->OSPEEDR &= ~(0x03U << (pin * 2U));
                /* Встановлення обраної крутості фронту */
                port->OSPEEDR |= (speed << (pin * 2U));
            }
        }
    }
}

/* Приклад налаштування плати для мінімізації EMI */
void board_optimize_emi_gpio(void)
{
    static const pin_emi_config_t emi_rules[] = {
        /* Світлодіод статусу та реле — мінімальна швидкість (2 МГц) */
        { GPIOC, (1U << 13) | (1U << 14), GPIO_SPEED_LOW_2MHZ },
        
        /* UART телеметрії (TX/RX) — мінімальна швидкість (2 МГц) */
        { GPIOA, (1U << 9) | (1U << 10), GPIO_SPEED_LOW_2MHZ },
        
        /* Шина I2C датчиків (SCL/SDA, 400 кГц) — помірна швидкість (25 МГц) */
        { GPIOB, (1U << 6) | (1U << 7), GPIO_SPEED_MEDIUM_25MHZ },
        
        /* Тактовий сигнал SPI флеш-пам'яті (SCK, 20 МГц) — швидкість 50 МГц */
        { GPIOA, (1U << 5), GPIO_SPEED_FAST_50MHZ }
    };

    gpio_configure_slew_rate(emi_rules, sizeof(emi_rules) / sizeof(emi_rules[0]));
}
