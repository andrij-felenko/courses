#include "esp_timer.h"

static int64_t last_step_us = 0;         // коли зробили попередній крок (мкс)
static int64_t step_interval_us = 2000;  // період між півкроками
static int dir = +1;

static void motor_task(void *arg) {
  for (;;) {
    int64_t now = esp_timer_get_time();   // мкс від старту, 64 біти
    if (now - last_step_us >= step_interval_us) {
      last_step_us = now;
      if (dir > 0) idx = (idx + 1) % 8;
      else         idx = (idx + 7) % 8;
      apply_step(idx);
    }
    vTaskDelay(1);   // ...а тут процесор віддано іншим задачам: кнопки, Wi-Fi, UART...
  }
}
