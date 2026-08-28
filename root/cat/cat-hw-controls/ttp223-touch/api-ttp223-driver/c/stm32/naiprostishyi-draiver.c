#include "stm32f4xx_hal.h"
#include <stdio.h>

#define TOUCH_PORT  GPIOA              // SIG давача TTP223 на PA0
#define TOUCH_PIN   GPIO_PIN_0

static void touch_init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin  = TOUCH_PIN;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_NOPULL;                  // вихід двотактний → без підтяжки
    HAL_GPIO_Init(TOUCH_PORT, &gpio);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    touch_init();

    while (1) {
        bool touched = (HAL_GPIO_ReadPin(TOUCH_PORT, TOUCH_PIN) == GPIO_PIN_SET);
        printf("%s\r\n", touched ? "палець" : "-");   // вивід у UART/SWO
        HAL_Delay(100);
    }
}
