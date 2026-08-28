// Той самий LEDC, але штатним драйвером ESP-IDF: жодних обгорток
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BUZ      GPIO_NUM_25
#define DUTY_50  512            // 50 % при 10-бітній роздільній здатності

static void play_note(uint32_t freq, uint32_t ms) {
  if (freq == 0) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);      // 0 Гц → тиша
  } else {
    ledc_set_freq(LEDC_LOW_SPEED_MODE, LEDC_TIMER_0, freq);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, DUTY_50); // 50 %-меандр
  }
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
  vTaskDelay(pdMS_TO_TICKS(ms));                 // (у бойовому коді — задача!)
  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void app_main(void) {
  buzzer_init();                 // ledc_timer_config + ledc_channel_config, як вище
  while (1) {
    play_note(523, 200);         // до
    play_note(659, 200);         // мі
    play_note(784, 400);         // соль
    vTaskDelay(pdMS_TO_TICKS(2000));
  }
}
