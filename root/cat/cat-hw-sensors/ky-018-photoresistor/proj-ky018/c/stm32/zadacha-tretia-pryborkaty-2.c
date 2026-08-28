#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef  hadc1;    // ADC1, вхід IN0 → PA0
extern UART_HandleTypeDef huart2;

#define N 16                        // розмір вікна

static int     buf[N];              // кільцевий буфер відліків
static uint8_t idx = 0;             // куди писати наступний
static long    sum = 0;             // поточна сума вмісту буфера
static bool    filled = false;      // чи буфер уже повний

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

static int moving_average(int raw) {
  sum -= buf[idx];                  // викинути найдавніший відлік із суми
  buf[idx] = raw;                   // покласти новий на його місце
  sum += raw;                       // додати новий у суму
  idx = (idx + 1) % N;              // зсунути вказівник по колу
  if (idx == 0) filled = true;
  uint8_t count = filled ? N : idx; // поки не заповнилось — ділимо на реальну кількість
  return count ? (int)(sum / count) : raw;
}

void ldr_loop(void) {               // кликати з main() після MX_*_Init()
  char line[24];
  for (;;) {
    int raw = ldr_read();
    int n = snprintf(line, sizeof line, "%d\r\n", moving_average(raw));
    HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
    HAL_Delay(20);
  }
}
