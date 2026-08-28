#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define TOUCH_PORT  GPIOC
#define TOUCH_PIN   GPIO_PIN_0    // SIG давача TTP223
#define LED_PORT    GPIOA
#define LED_PIN     GPIO_PIN_5    // світлодіод плати

static void GPIO_Init(void) {
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef in = {
        .Pin  = TOUCH_PIN,
        .Mode = GPIO_MODE_INPUT,
        .Pull = GPIO_NOPULL,      // вихід двотактний — підтяжка не потрібна
    };
    HAL_GPIO_Init(TOUCH_PORT, &in);

    GPIO_InitTypeDef out = {
        .Pin   = LED_PIN,
        .Mode  = GPIO_MODE_OUTPUT_PP,
        .Pull  = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
    };
    HAL_GPIO_Init(LED_PORT, &out);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();         // згенерований CubeMX
    GPIO_Init();

    while (1) {
        // активний у 1: дотик = GPIO_PIN_SET
        GPIO_PinState touched = HAL_GPIO_ReadPin(TOUCH_PORT, TOUCH_PIN);
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, touched);
        HAL_Delay(20);
    }
}
