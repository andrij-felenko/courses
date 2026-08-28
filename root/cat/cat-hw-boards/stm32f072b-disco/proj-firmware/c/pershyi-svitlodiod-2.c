#include "stm32f0xx_hal.h"

int main(void) {
    HAL_Init();
    SystemClock_Config();                        // згенерований аналог clock_48mhz()

    __HAL_RCC_GPIOC_CLK_ENABLE();                // те саме тактування GPIOC — лише іменем

    GPIO_InitTypeDef led = {0};
    led.Pin   = GPIO_PIN_6;                       // PC6 = LD3
    led.Mode  = GPIO_MODE_OUTPUT_PP;             // push-pull вихід
    led.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &led);

    for (;;) {
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_6);   // перемкнути LD3
        HAL_Delay(500);                          // 500 мс, рахує системний таймер
    }
}
