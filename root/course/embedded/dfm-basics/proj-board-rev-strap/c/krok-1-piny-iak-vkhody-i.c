#include "stm32f4xx_hal.h"

// Три страпи ревізії на порту C: PC13=REV2, PC14=REV1, PC15=REV0.
#define REV_PORT   GPIOC
#define REV2_PIN   GPIO_PIN_13
#define REV1_PIN   GPIO_PIN_14
#define REV0_PIN   GPIO_PIN_15

// Налаштувати три піни як входи БЕЗ підтяжки:
// рівень задає лише зовнішній резистор на платі.
static void rev_straps_init(void) {
    __HAL_RCC_GPIOC_CLK_ENABLE();          // без такту на порт GPIO мовчить

    GPIO_InitTypeDef g = {0};
    g.Pin  = REV2_PIN | REV1_PIN | REV0_PIN;
    g.Mode = GPIO_MODE_INPUT;              // цифровий вхід
    g.Pull = GPIO_NOPULL;                  // ← КЛЮЧОВЕ: жодної внутрішньої підтяжки
    HAL_GPIO_Init(REV_PORT, &g);
}
