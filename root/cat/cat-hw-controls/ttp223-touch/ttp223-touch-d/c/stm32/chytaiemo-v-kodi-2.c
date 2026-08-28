#include "stm32f4xx_hal.h"
#include <stdbool.h>
#include <stdio.h>

#define TOUCH_PORT  GPIOC
#define TOUCH_PIN   GPIO_PIN_0

int main(void) {
    HAL_Init();
    SystemClock_Config();         // згенерований CubeMX
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef in = {
        .Pin  = TOUCH_PIN,
        .Mode = GPIO_MODE_INPUT,
        .Pull = GPIO_NOPULL,
    };
    HAL_GPIO_Init(TOUCH_PORT, &in);

    bool     prev  = false;       // попередній стан входу
    uint32_t count = 0;           // скільки разів торкнулися

    while (1) {
        bool now = (HAL_GPIO_ReadPin(TOUCH_PORT, TOUCH_PIN) == GPIO_PIN_SET);
        if (now && !prev) {       // щойно був 0, тепер 1 → фронт, момент дотику
            count++;
            printf("дотиків: %lu\r\n", (unsigned long)count);  // printf → UART
        }
        prev = now;
        HAL_Delay(20);
    }
}
