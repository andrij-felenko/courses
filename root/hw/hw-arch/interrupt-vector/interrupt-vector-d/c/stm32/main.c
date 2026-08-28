#include "main.h"                     // згенерований заголовок HAL
#include <stdbool.h>
#include <stdio.h>                    // printf перенаправлено на UART

volatile bool pressed = false;        // ISR і main() бачать ту саму змінну

// Вектор EXTI0 → HAL_GPIO_EXTI_IRQHandler() → цей колбек
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
  if (pin == GPIO_PIN_0) pressed = true;   // одна дешева дія — і все
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  GPIO_InitTypeDef cfg = {0};
  cfg.Pin  = GPIO_PIN_0;
  cfg.Mode = GPIO_MODE_IT_FALLING;    // спад: кнопка тягне вхід до землі
  cfg.Pull = GPIO_PULLUP;             // підтяжка догори: у спокої вхід високий
  HAL_GPIO_Init(GPIOA, &cfg);

  HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);  // NVIC: пріоритет і дозвіл
  HAL_NVIC_EnableIRQ(EXTI0_IRQn);

  while (1) {                         // важку роботу робимо ТУТ, поза ISR
    if (pressed) {
      pressed = false;
      printf("кнопку натиснуто\r\n");
    }
  }
}
