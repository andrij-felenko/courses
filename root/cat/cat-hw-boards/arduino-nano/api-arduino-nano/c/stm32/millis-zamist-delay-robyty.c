#include "stm32f4xx_hal.h"
#include <stdio.h>

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();

    uint32_t ledLast = 0, msgLast = 0;   // коли востаннє робили кожну дію
    GPIO_PinState led = GPIO_PIN_RESET;

    while (1) {
        uint32_t now = HAL_GetTick();    // мілісекунди від старту

        // задача 1: блимати раз на секунду, нікого не блокуючи
        if (now - ledLast >= 1000) {
            ledLast = now;
            led = (led == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, led);
        }

        // задача 2: слати число щопівсекунди
        if (now - msgLast >= 500) {
            msgLast = now;
            printf("%lu\r\n", (unsigned long)now);
        }

        // задача 3: кнопка реагує МИТТЄВО — жодного HAL_Delay її не глушить
        if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET) {
            // тут дія на натискання
        }
    }
}
