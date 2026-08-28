#include "main.h"

// Спільний катод — на канал таймера в режимі PWM Generation (CubeMX: TIM3_CH1,
// період лічильника 255, частота ≈1 кГц). Далі шпаруватість тримає таймер.
extern TIM_HandleTypeDef htim3;

static void brightness_begin(void) {
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
}

// Катод світить НИЗЬКИМ рівнем → яскравість = час, коли вихід унизу.
static void set_brightness(uint8_t b) {
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 255 - b);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM3_Init();
  brightness_begin();
  seg_show_hex(0x3, false);          // показуємо «3»
  set_brightness(128);               // половина яскравості
  while (1) { }                      // ядро вільне: ШІМ іде сам
}
