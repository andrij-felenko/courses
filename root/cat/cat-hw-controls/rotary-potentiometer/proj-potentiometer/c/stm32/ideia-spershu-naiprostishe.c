#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;           // CubeMX: ADC1, канал IN0 = PA0, роздільність 12 біт
#define ADC_MAX 4095

static uint16_t potSample(void) {         // один вимір: старт → дочекатись → забрати
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);  // стеля очікування 10 мс
  uint16_t v = (uint16_t)HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_ADC1_Init();
  MX_USART2_UART_Init();                  // printf перенаправлено на UART2

  while (1) {
    uint16_t raw = potSample();           // 0..4095: сира частка ходу
    int pct = raw * 100 / ADC_MAX;        // та сама пропорція, тільки руками
    printf("%u  ->  %d %%\r\n", raw, pct);
    HAL_Delay(100);
  }
}
