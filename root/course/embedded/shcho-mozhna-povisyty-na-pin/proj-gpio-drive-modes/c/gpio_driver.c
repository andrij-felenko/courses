/* Файл: gpio_driver.c — Реалізація мовою C (STM32 LL API) */
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"
#include <stdbool.h>

/* Структура конфігурації піна */
typedef struct {
    GPIO_TypeDef *port;
    uint32_t pin_mask;
    bool active_low;
} GpioOutputConfig;

/* Ініціалізація виводу в безпечному режимі з мінімальною швидкістю */
void gpio_output_init(const GpioOutputConfig *cfg)
{
    /* 1. Тактування порту */
    if (cfg->port == GPIOA) {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    } else if (cfg->port == GPIOB) {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
    } else if (cfg->port == GPIOC) {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOC);
    }

    /* 2. Початковий безпечний стан виводу ДО ввімкнення режиму OUTPUT */
    if (cfg->active_low) {
        LL_GPIO_SetOutputPin(cfg->port, cfg->pin_mask);   /* Пасивний стан: 3.3 В */
    } else {
        LL_GPIO_ResetOutputPin(cfg->port, cfg->pin_mask); /* Пасивний стан: 0 В */
    }

    /* 3. Налаштування вихідного каскаду */
    LL_GPIO_InitTypeDef init_struct;
    init_struct.Pin        = cfg->pin_mask;
    init_struct.Mode       = LL_GPIO_MODE_OUTPUT;
    init_struct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    init_struct.Speed      = LL_GPIO_SPEED_FREQ_LOW; /* Захист від Ground Bounce! */
    init_struct.Pull       = LL_GPIO_PULL_NO;

    LL_GPIO_Init(cfg->port, &init_struct);
}

void gpio_output_set(const GpioOutputConfig *cfg, bool turn_on)
{
    bool drive_high = cfg->active_low ? !turn_on : turn_on;
    if (drive_high) {
        LL_GPIO_SetOutputPin(cfg->port, cfg->pin_mask);
    } else {
        LL_GPIO_ResetOutputPin(cfg->port, cfg->pin_mask);
    }
}
