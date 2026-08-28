/* TIM3_CH1 у режимі PWM з ARR = 255 — тоді регістр порівняння CCR1 і є
   яскравість 0..255, точнісінько як аргумент analogWrite. */
#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;           // ADC1, канал IN0 = PA0 (повзунок)
extern TIM_HandleTypeDef htim3;           // TIM3_CH1 = PA6 (світлодіод)

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_ADC1_Init();
  MX_TIM3_Init();
  MX_USART2_UART_Init();
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);

  pot_t pot;
  pot_begin(&pot, &hadc1, 4, 16);         // SHIFT=4 (α≈0.06), мертва зона 16 (12 біт!)

  // 3-секундне калібрування: крути ручку від упору до упору.
  printf("Калібрування: крути ручку від краю до краю...\r\n");
  uint32_t t0 = HAL_GetTick();
  while (HAL_GetTick() - t0 < 3000) { pot_calibrate(&pot); HAL_Delay(5); }
  printf("Готово.\r\n");

  while (1) {
    int bright;
    // яскравість 0..255; подія лише коли ручку реально крутнули
    if (pot_changed(&pot, &bright, 0, 255)) {
      __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, bright);
      printf("яскравість = %d\r\n", bright);
    }
    HAL_Delay(10);
  }
}
