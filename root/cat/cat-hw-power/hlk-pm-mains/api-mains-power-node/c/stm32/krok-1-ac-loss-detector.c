/* ============================================================================
   krok-1-ac-loss-detector.c — STM32 HAL: моніторинг наявності мережі 220 В
   ========================================================================== */

#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define ZC_PIN              GPIO_PIN_0
#define ZC_PORT             GPIOA
#define AC_LOSS_TIMEOUT_MS  15    // При 50 Гц імпульс кожні 10 мс

static volatile uint32_t s_last_zc_tick = 0;
static volatile bool     s_ac_power_good = false;

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == ZC_PIN) {
        s_last_zc_tick = HAL_GetTick();
        s_ac_power_good = true;
    }
}

void mains_detector_init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef gpio_init = {0};
    gpio_init.Pin = ZC_PIN;
    gpio_init.Mode = GPIO_MODE_IT_FALLING;
    gpio_init.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(ZC_PORT, &gpio_init);

    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0); // Найвищий пріоритет переривання
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

    s_last_zc_tick = HAL_GetTick();
}

bool mains_is_ac_present(void) {
    if ((HAL_GetTick() - s_last_zc_tick) > AC_LOSS_TIMEOUT_MS) {
        s_ac_power_good = false;
    }
    return s_ac_power_good;
}
