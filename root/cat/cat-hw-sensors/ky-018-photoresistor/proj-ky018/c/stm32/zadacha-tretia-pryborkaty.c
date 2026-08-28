#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef  hadc1;    // CubeMX: ADC1, вхід IN0 → PA0, 12 біт
extern UART_HandleTypeDef huart2;   // куди друкуємо замість Serial

#define ALPHA 0.2f                  // 0.1 гладше+лінивіше · 0.5 жвавіше+шумніше

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

void ldr_loop(void) {               // кликати з main() після MX_*_Init()
  float smoothed = ldr_read();      // засіяти першим відліком, а не нулем
  char line[24];
  for (;;) {
    uint16_t raw = ldr_read();
    smoothed += ALPHA * (raw - smoothed);   // y ← y + α·(нове − y)
    int n = snprintf(line, sizeof line, "%d\r\n", (int)smoothed);
    HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
    HAL_Delay(20);
  }
}
