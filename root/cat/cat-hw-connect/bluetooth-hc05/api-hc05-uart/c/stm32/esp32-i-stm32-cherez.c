// STM32 HAL: CubeMX уже згенерував huart1 (модуль, 9600 8N1)
// і huart2 (монітор через ST-Link VCP). Плата на 3.3 В → без дільника.
#include "main.h"

extern UART_HandleTypeDef huart1;   // модуль
extern UART_HandleTypeDef huart2;   // монітор

// Викликати з головного циклу. Тайм-аут 10 мс на прийом означає:
// байта немає — не чекаємо, а йдемо перевіряти зустрічний напрям.
void bt_bridge(void) {
    uint8_t b;

    if (HAL_UART_Receive(&huart1, &b, 1, 10) == HAL_OK)   // модуль → монітор
        HAL_UART_Transmit(&huart2, &b, 1, 100);

    if (HAL_UART_Receive(&huart2, &b, 1, 10) == HAL_OK)   // монітор → модуль
        HAL_UART_Transmit(&huart1, &b, 1, 100);

    // Опитування придатне для 9600. На вищих швидкостях беріть
    // HAL_UART_Receive_IT / _DMA у кільцевий буфер, інакше губитимете байти.
}
