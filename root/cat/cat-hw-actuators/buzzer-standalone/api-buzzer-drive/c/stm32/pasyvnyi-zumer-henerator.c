#include "main.h"               // CubeMX: TIM3_CH1 у режимі PWM Generation → зумер
// NOTE_C4…NOTE_C5, NOTE_REST — та сама таблиця частот, що у вкладці Arduino

extern TIM_HandleTypeDef htim3;

// Частоту меандру задає ARR, шпаруватість 50 % — CCR = (ARR+1)/2
static void tone_hz(uint32_t hz) {
  if (hz == NOTE_REST) { HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1); return; }
  uint32_t tim_clk = HAL_RCC_GetPCLK1Freq() * 2;      // такт таймерів APB1
  uint32_t arr = tim_clk / ((htim3.Init.Prescaler + 1) * hz) - 1;
  __HAL_TIM_SET_AUTORELOAD(&htim3, arr);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, (arr + 1) / 2);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
}

// Одна нота: увімкнути частоту, витримати, вимкнути
static void play_note(uint32_t freq, uint32_t ms) {
  tone_hz(freq);
  HAL_Delay(ms);
  tone_hz(NOTE_REST);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM3_Init();

  while (1) {
    play_note(NOTE_C4, 200);
    play_note(NOTE_E4, 200);
    play_note(NOTE_G4, 200);
    play_note(NOTE_C5, 400);
    HAL_Delay(2000);
  }
}
