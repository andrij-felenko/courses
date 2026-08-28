// Те саме на STM32 HAL. Ніжку в CubeMX ставимо входом із внутрішньою
// підтяжкою вгору (GPIO_MODE_INPUT + GPIO_PULLUP), якщо зовнішньої нема.
#include "main.h"
#include <string.h>

extern UART_HandleTypeDef huart2;

#define FS_PORT  GPIOA
#define FS_PIN   GPIO_PIN_1

int main(void) {
  HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();

  while (1) {
    if (HAL_GPIO_ReadPin(FS_PORT, FS_PIN) == GPIO_PIN_RESET) {
      // Драйвер сам знеструмив міст і сигналить біду.
      // Найчастіша причина при першому запуску — V+ без напруги
      // або просадка живлення; далі — перегрів чи КЗ на виході.
      const char *msg = "MC33886: FAULT (перевір V+, землю, струм, нагрів)\r\n";
      HAL_UART_Transmit(&huart2, (const uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
      HAL_Delay(500);
    }
    HAL_Delay(10);
  }
}
