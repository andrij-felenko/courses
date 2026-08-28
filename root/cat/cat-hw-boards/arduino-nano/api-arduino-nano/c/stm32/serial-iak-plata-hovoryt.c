#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <string.h>

extern UART_HandleTypeDef huart2;   // 9600 бод виставлено в CubeMX

static void tx(const char *s) {     // передати рядок і дочекатися кінця
    HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), HAL_MAX_DELAY);
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();
    tx("Готовий\r\n");

    uint32_t last = 0;
    while (1) {
        uint8_t cmd;                // приймання: одна літера-команда
        if (HAL_UART_Receive(&huart2, &cmd, 1, 10) == HAL_OK) {
            if (cmd == '1') HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
            if (cmd == '0') HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
        }
        uint32_t now = HAL_GetTick();   // мілісекунди від старту
        if (now - last >= 1000) {       // передавання: показник щосекунди
            last = now;
            char line[32];
            snprintf(line, sizeof line, "лічильник = %lu\r\n",
                     (unsigned long)(now / 1000));
            tx(line);
        }
    }
}
