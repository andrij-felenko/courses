// KY-009, спільний катод. R→TIM3_CH1, G→TIM3_CH2, B→TIM3_CH3 (кожен ЧЕРЕЗ резистор); − → GND.
// Таймер налаштовано в CubeMX як PWM Generation, ARR = 255 → шпаруватість теж 0…255.
#include "main.h"

extern TIM_HandleTypeDef htim3;

static void rgb_start(void) {
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);   // червоний
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);   // зелений
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);   // синій
}

static void rgb_set(uint8_t r, uint8_t g, uint8_t b) {
  // Запис у регістр порівняння каналу — це і є «задати яскравість».
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, r);   // спільний катод → більше = яскравіше
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, g);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, b);
}

// у main(), після MX_TIM3_Init():
//   rgb_start();
//   rgb_set(255, 128, 0);   // помаранчевий: повний червоний, півзеленого, без синього
