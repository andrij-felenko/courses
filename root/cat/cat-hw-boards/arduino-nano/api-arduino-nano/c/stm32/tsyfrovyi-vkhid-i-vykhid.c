#include "stm32f4xx_hal.h"

// кнопка між PC13 і GND, світлодіод на PA5
int main(void) {
    HAL_Init(); SystemClock_Config();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef btn = {
        .Pin  = GPIO_PIN_13,
        .Mode = GPIO_MODE_INPUT,
        .Pull = GPIO_PULLUP,              // вільний стан = 1, натиск = 0
    };
    HAL_GPIO_Init(GPIOC, &btn);

    GPIO_InitTypeDef led = {
        .Pin = GPIO_PIN_5, .Mode = GPIO_MODE_OUTPUT_PP,
        .Pull = GPIO_NOPULL, .Speed = GPIO_SPEED_FREQ_LOW,
    };
    HAL_GPIO_Init(GPIOA, &led);

    while (1) {
        // натиснуто = замкнуто на GND
        bool pressed = (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5,
                          pressed ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }
}
