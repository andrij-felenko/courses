#include "main.h"                  // HALL_Pin / LED_Pin — імена з CubeMX

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef gi = {0};
    gi.Pin  = HALL_Pin;            // PA0 — S давача KY-003
    gi.Mode = GPIO_MODE_INPUT;
    gi.Pull = GPIO_PULLUP;         // без підтяжки нога висить — читатимеш сміття
    HAL_GPIO_Init(HALL_GPIO_Port, &gi);

    gi.Pin   = LED_Pin;            // PC13 — світлодіод плати
    gi.Mode  = GPIO_MODE_OUTPUT_PP;
    gi.Pull  = GPIO_NOPULL;
    gi.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LED_GPIO_Port, &gi);

    while (1) {
        // вихід активний у нулі: GPIO_PIN_RESET = є магніт
        bool magnet = (HAL_GPIO_ReadPin(HALL_GPIO_Port, HALL_Pin) == GPIO_PIN_RESET);
        HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, magnet ? GPIO_PIN_SET : GPIO_PIN_RESET);
        if (magnet) printf("магніт!\r\n");
        HAL_Delay(50);
    }
}
