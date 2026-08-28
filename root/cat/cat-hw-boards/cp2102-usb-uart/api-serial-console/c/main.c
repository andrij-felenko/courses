#include <stdio.h>
#include "stm32f0xx_hal.h"

extern UART_HandleTypeDef huart1;   // USART1 налаштований у CubeMX: 115200 8N1

// Гачок стандартної бібліотеки: printf врешті кличе саме сюди для КОЖНОГО символу.
// Перевизначаємо його — і весь printf/putchar починає йти в UART.
// (Ім'я функції залежить від toolchain: у newlib це _write, у деяких — __io_putchar.)
int __io_putchar(int ch)
{
    // блокуюча передача одного байта; HAL_MAX_DELAY = чекати, поки передавач звільниться
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();   // згенеровано CubeMX
    MX_GPIO_Init();
    MX_USART1_UART_Init();  // тут USART1 і піднімається на 115200 8N1

    int t = 0;
    while (1) {
        // звичайнісінький printf — а рядок виходить на ніжку TX (PA9)
        printf("темп = %d C\r\n", t);
        t = (t + 1) % 100;
        HAL_Delay(1000);    // раз на секунду
    }
}
