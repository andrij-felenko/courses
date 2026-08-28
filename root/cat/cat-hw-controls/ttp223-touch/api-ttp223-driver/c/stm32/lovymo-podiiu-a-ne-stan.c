#include "stm32f4xx_hal.h"
#include <stdio.h>

#define TOUCH_PORT  GPIOA
#define TOUCH_PIN   GPIO_PIN_0

int main(void) {
    HAL_Init();
    SystemClock_Config();
    touch_init();                  // той самий GPIO_MODE_INPUT + GPIO_NOPULL

    bool     prev  = false;        // стан входу з минулого проходу циклу
    uint32_t count = 0;

    while (1) {
        bool now = (HAL_GPIO_ReadPin(TOUCH_PORT, TOUCH_PIN) == GPIO_PIN_SET);

        if (now && !prev) {        // було 0, стало 1 → передній фронт = момент дотику
            count++;
            printf("дотиків: %lu\r\n", (unsigned long)count);
        }
        // if (!now && prev) { … } // тут ловився б задній фронт = момент відпускання

        prev = now;                // запам'ятали для наступного проходу
        HAL_Delay(20);
    }
}
