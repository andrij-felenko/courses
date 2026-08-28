#include "main.h"
#include <stdlib.h>
#include <stdio.h>

extern TIM_HandleTypeDef  htim3;
extern UART_HandleTypeDef huart2;

// Калібрувальні межі КОНКРЕТНОГО серва — знайдені дослідом (див. нижче).
#define US_MIN 1000                 // ширина для 0°
#define US_MAX 2000                 // ширина для 180°

// Наш власний перерахунок кут → мікросекунди за ВІДКАЛІБРОВАНИМИ межами.
static int deg_to_us(int deg) {
  if (deg < 0)   deg = 0;
  if (deg > 180) deg = 180;
  return US_MIN + deg * (US_MAX - US_MIN) / 180;   // лінійно між нашими межами
}

int main(void) {
  HAL_Init(); SystemClock_Config();
  MX_GPIO_Init(); MX_TIM3_Init(); MX_USART2_UART_Init();
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);

  char line[8], msg[48];
  uint8_t len = 0, ch;
  while (1) {
    // Приймаємо кут із порту посимвольно: число 0..180 і Enter.
    if (HAL_UART_Receive(&huart2, &ch, 1, 10) != HAL_OK) continue;
    if (ch != '\r' && ch != '\n') {
      if (len < sizeof(line) - 1) line[len++] = ch;
      continue;
    }
    if (len == 0) continue;
    line[len] = 0; len = 0;
    int deg = atoi(line);
    if (deg < 0 || deg > 180) continue;
    int us = deg_to_us(deg);
    servo_write_us(us);
    int m = snprintf(msg, sizeof(msg), "кут %d -> %d мкс\r\n", deg, us);
    HAL_UART_Transmit(&huart2, (uint8_t *)msg, m, 100);
  }
}
