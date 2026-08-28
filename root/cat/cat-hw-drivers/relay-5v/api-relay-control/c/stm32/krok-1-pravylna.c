// Те саме на STM32 HAL: запис в ODR СПЕРШУ, HAL_GPIO_Init — ПОТІМ.
#include "stm32f4xx_hal.h"

#define RELAY_PORT  GPIOB
#define RELAY_PIN   GPIO_PIN_5
#define RELAY_ON    GPIO_PIN_RESET   // active-low: нуль вмикає
#define RELAY_OFF   GPIO_PIN_SET     // одиниця вимикає

void relay_init(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE();

    // 1) СПЕРШУ рівень OFF у засувку ODR — ніжка ще вхід, назовні нічого не йде.
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, RELAY_OFF);

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin   = RELAY_PIN;
    gpio.Mode  = GPIO_MODE_OUTPUT_PP;   // 2) ТІЛЬКИ ТЕПЕР — вихід
    gpio.Pull  = GPIO_NOPULL;           // вікно до цього рядка закриває
    gpio.Speed = GPIO_SPEED_FREQ_LOW;   // ЗОВНІШНЯ підтяжка на IN (див. нижче)
    HAL_GPIO_Init(RELAY_PORT, &gpio);
    // Драйвер вмикається вже з рівнем OFF — старт тихий.
}
