// STM32 HAL: та сама рутина — у перериванні апаратного таймера, зведеного на 1 кГц
extern TIM_HandleTypeDef htim6;

void shield_tick(void);               // один розряд, опитування кнопок, відлік писку

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                     // латч/такт/дані — виходи, кнопки — входи з підтяжкою
  MX_TIM6_Init();                     // прескалер і період дають 1 кГц
  HAL_TIM_Base_Start_IT(&htim6);      // з цієї миті дисплей ведеться сам

  while (1) { /* тут лише логіка */ }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance == TIM6) shield_tick();
}
