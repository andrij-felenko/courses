#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
// NOTE_C4…NOTE_C5, NOTE_REST — та сама таблиця частот, що у вкладці Arduino

#define BUZ      GPIO_NUM_18
#define DUTY_50  512            // 50 % при 10-бітній роздільній здатності

static void buzzer_init(void) {
  ledc_timer_config_t t = {
    .speed_mode      = LEDC_LOW_SPEED_MODE,
    .duty_resolution = LEDC_TIMER_10_BIT,
    .timer_num       = LEDC_TIMER_0,
    .freq_hz         = 1000,    // стартова, далі переб'ється нотою
    .clk_cfg         = LEDC_AUTO_CLK,
  };
  ledc_timer_config(&t);
  ledc_channel_config_t c = {
    .gpio_num   = BUZ,
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel    = LEDC_CHANNEL_0,
    .timer_sel  = LEDC_TIMER_0,
    .duty       = 0,            // старт із тиші
    .hpoint     = 0,
  };
  ledc_channel_config(&c);
}

// Увімкнути меандр заданої частоти; 0 Гц → тиша
static void buzzer_tone(uint32_t freq) {
  if (freq == NOTE_REST) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
  } else {
    ledc_set_freq(LEDC_LOW_SPEED_MODE, LEDC_TIMER_0, freq);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, DUTY_50);
  }
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

// Одна нота: увімкнути частоту, витримати, вимкнути
static void play_note(uint32_t freq, uint32_t ms) {
  buzzer_tone(freq);
  vTaskDelay(pdMS_TO_TICKS(ms));
  buzzer_tone(NOTE_REST);
}

void app_main(void) {
  buzzer_init();
  while (1) {
    play_note(NOTE_C4, 200);
    play_note(NOTE_E4, 200);
    play_note(NOTE_G4, 200);
    play_note(NOTE_C5, 400);
    vTaskDelay(pdMS_TO_TICKS(2000));
  }
}
