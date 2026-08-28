#include "main.h"                   // htim3: канал TIM3_CH1 виведено на зумер

#define NOTE_C5  523
#define NOTE_E5  659
#define NOTE_G5  784

extern TIM_HandleTypeDef htim3;
#define TIM_CLK_HZ  1000000u        // дільник у CubeMX дає таймеру рівно 1 МГц

static void play_note(uint32_t freq, uint32_t ms) {
  uint32_t arr = TIM_CLK_HZ / freq - 1;                   // період = ця нота
  __HAL_TIM_SET_AUTORELOAD(&htim3, arr);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, arr / 2);  // 50 % — меандр
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);               // таймер жене хвилю
  HAL_Delay(ms);                                          // тримаємо ноту
  HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1);                // тиша
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM3_Init();                   // канал у режимі PWM, вивід — альтернативна функція
  while (1) {
    play_note(NOTE_C5, 200);        // до
    play_note(NOTE_E5, 200);        // мі
    play_note(NOTE_G5, 300);        // соль — простенький акорд «по черзі»
    HAL_Delay(1500);
  }
}
