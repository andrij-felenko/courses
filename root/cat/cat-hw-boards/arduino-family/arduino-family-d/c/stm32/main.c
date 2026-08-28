/* main.c — той самий блимач на STM32 HAL */
#include "stm32f4xx_hal.h"

#define LED_PORT GPIOA
#define LED_PIN  GPIO_PIN_5

int main(void)
{
    HAL_Init();
    SystemClock_Config();                  // тактування ядра (згенерував CubeMX)

    __HAL_RCC_GPIOA_CLK_ENABLE();          // без такту порт мовчить
    GPIO_InitTypeDef io = {0};             // налаштування виводу: «раз при старті»
    io.Pin   = LED_PIN;
    io.Mode  = GPIO_MODE_OUTPUT_PP;
    io.Pull  = GPIO_NOPULL;
    io.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LED_PORT, &io);

    while (1) {                            // вічний цикл пишемо самі
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
        HAL_Delay(500);
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
        HAL_Delay(500);
    }
}
