/* DO_GPIO_Port / DO_Pin налаштовано в CubeMX як GPIO_Input, Pull-up/Pull-down = None:
   підтяжка вже стоїть на платі модуля */
#include "main.h"
#include <stdio.h>

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();             // printf перенаправлено на UART

    while (1) {
        GPIO_PinState level = HAL_GPIO_ReadPin(DO_GPIO_Port, DO_Pin);   // сирий рівень
        printf("%s\r\n", level == GPIO_PIN_SET ? "DO = HIGH" : "DO = LOW");
        HAL_Delay(300);
    }
}
