#include "esp_rom_sys.h"   // esp_rom_delay_us()

// Готової бібліотеки нема — обгортка над рівнем 1. Уся «магія» Stepper
// зводиться ось до цього масиву: виводи в МАГНІТНОМУ порядку 1-3-2-4,
// а не так, як ідуть дроти (IN1=GPIO18, IN3=GPIO21, IN2=GPIO19, IN4=GPIO22).
static const gpio_num_t MAG[4] = { IN1, IN3, IN2, IN4 };

#define STEPS_PER_REV 2038   // ПОВНИХ кроків вала, ≈ 32 · 63.684 (НЕ 2048!)

// Повнокрокова послідовність (саме її ганяє Stepper): по дві сусідні обмотки.
static const uint8_t full_seq[4][4] = {
  {1,1,0,0}, {0,1,1,0}, {0,0,1,1}, {1,0,0,1},
};

static uint32_t step_us = 60000000UL / (10 * STEPS_PER_REV);   // 10 об/хв

static void stepper_step(long steps) {
  static int s = 0;
  int dir = steps > 0 ? +1 : -1;
  for (long i = 0; i < labs(steps); i++) {
    s = (s + dir + 4) % 4;
    for (int k = 0; k < 4; k++) gpio_set_level(MAG[k], full_seq[s][k]);
    esp_rom_delay_us(step_us);
  }
}
