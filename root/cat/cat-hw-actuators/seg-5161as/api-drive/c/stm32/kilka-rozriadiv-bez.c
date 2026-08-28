#include "main.h"

// CubeMX: TIM2 з періодом 2 мс і ввімкненим перериванням → ~125 Гц на 4 розряди.
extern TIM_HandleTypeDef htim2;

// Вибір розряду: 4 ноги, налаштовані як GPIO_Output у MX_GPIO_Init().
static const SegPin DIGIT[4] = {
  {GPIOB, GPIO_PIN_0}, {GPIOB, GPIO_PIN_1},
  {GPIOB, GPIO_PIN_2}, {GPIOB, GPIO_PIN_3},
};
static volatile uint8_t frame[4] = { 0, 0, 0, 0 };

// Один розряд за переривання — той самий порядок кроків, що й у циклі.
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance != TIM2) return;
  static uint8_t d = 0;
  for (int i = 0; i < 4; i++)                                 // згасити все
    HAL_GPIO_WritePin(DIGIT[i].port, DIGIT[i].pin, GPIO_PIN_SET);
  seg_show_mask(frame[d]);                                    // маска розряду
  HAL_GPIO_WritePin(DIGIT[d].port, DIGIT[d].pin, GPIO_PIN_RESET);  // катод на землю
  d = (d + 1) & 3;
}

static void set_number(int n) {
  for (int d = 3; d >= 0; d--) { frame[d] = FONT[n % 10]; n /= 10; }
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM2_Init();
  set_number(1234);
  HAL_TIM_Base_Start_IT(&htim2);      // далі перемальовує переривання
  while (1) { }
}
