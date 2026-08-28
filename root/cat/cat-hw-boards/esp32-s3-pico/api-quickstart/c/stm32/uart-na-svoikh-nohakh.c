#include "stm32f4xx_hal.h"

extern UART_HandleTypeDef huart1;   // зовнішній пристрій; 9600 8N1 задано в MX_USART1_UART_Init()
extern UART_HandleTypeDef huart2;   // журнал у комп'ютер через перехідник USB↔UART

void forward_forever(void) {
  uint8_t b;
  while (1) {
    if (HAL_UART_Receive(&huart1, &b, 1, 20) == HAL_OK)  // прийшов байт
      HAL_UART_Transmit(&huart2, &b, 1, 10);             // пересилаємо його в журнал
  }
}
