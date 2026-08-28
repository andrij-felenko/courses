#include "stm32f4xx_hal.h"

UART_HandleTypeDef huart2;        // UART до модуля HC-05: TX→RX, RX→TX, спільна земля
                                  // ім'я задається модулю один раз: AT+NAME=STM32-robot

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_USART2_UART_Init();          // 9600 8N1 — заводський режим HC-05

  uint8_t c;
  while (1) {                     // модуль уже тримає SPP; для МК це звичайний UART
    if (HAL_UART_Receive(&huart2, &c, 1, HAL_MAX_DELAY) == HAL_OK)  // байт із радіо
      HAL_UART_Transmit(&huart2, &c, 1, HAL_MAX_DELAY);             // і назад (ехо)
  }
}
