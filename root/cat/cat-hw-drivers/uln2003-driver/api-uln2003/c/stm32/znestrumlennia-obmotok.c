// Рух завершує сам таймер, коли remaining дійде нуля, — там і гасимо обмотки:
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance != TIM2) return;
  if (remaining == 0) {
    HAL_TIM_Base_Stop_IT(&htim2);
    release_coils();              // доїхали — знеструмити обмотки
    return;
  }
  // ...далі як вище: крок, перерахунок швидкості, новий ARR
}
