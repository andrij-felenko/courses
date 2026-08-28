// TIM2, канал 1, ніжка PA0 (CubeMX: TIM2_CH1, PWM Generation CH1).
// Шина 72 МГц, PSC = 71 → лічильник цокає 1 МГц; ARR = 999 → період 1000 мкс = 1 кГц
extern TIM_HandleTypeDef htim2;

void pwm_start(void) {
  __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, 500);   // поріг 500/1000 = 50 %
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);            // і все
}

int main(void) {
  pwm_start();
  while (1) {
    // порожньо: сигнал іде сам; ядро вільне для будь-чого
  }
}
