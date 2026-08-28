// --- KY-016 на STM32 HAL: три канали ОДНОГО таймера ---
// TIM3 CH1/CH2/CH3 у режимі PWM Generation, ARR = 255 → шкала duty 0..255;
// частоту дає прескалер: f = f_TIM / (PSC+1) / (ARR+1) ≈ 5 кГц.
#include "main.h"

extern TIM_HandleTypeDef htim3;   // дескриптор таймера, згенерований CubeMX

#define COMMON_ANODE 0
#define DUTY_MAX 255              // = ARR таймера

// один вихід каналу: тут і тільки тут живе інверсія для анода
static inline uint32_t level(uint8_t v) {
  return COMMON_ANODE ? (uint32_t)(DUTY_MAX - v) : (uint32_t)v;
}

void set_color(uint8_t r, uint8_t g, uint8_t b) {
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, level(r));   // пишемо в CCR каналу
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, level(g));
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, level(b));
}

void rgb_init(void) {
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);   // пустити ШІМ на трьох каналах
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);
  set_color(255, 90, 0);                      // теплий помаранчевий
}
