// TIM6 (CubeMX: Prescaler 71 → лічильник 1 МГц, Period 999 → переповнення раз на 1 мс)
extern TIM_HandleTypeDef htim6;
volatile bool tick = false;          // прапорець «настала мить» — ставить ISR

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance == TIM6) tick = true;   // обробник: коротко, лише прапорець
}

int main(void) {
  /* … HAL_Init(), MX_TIM6_Init() з CubeMX … */
  HAL_TIM_Base_Start_IT(&htim6);     // відлік веде таймер, ядро вільне

  while (1) {
    if (tick) {                      // ядро реагує, коли зручно, а відлік — залізний
      tick = false;
      // тут — робота строго раз на мілісекунду
    }
  }
}
