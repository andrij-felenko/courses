#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BUZ      GPIO_NUM_18               // вивід із пасивним зумером
#define NOTE_C5  523
#define NOTE_E5  659
#define NOTE_G5  784

static void tone_init(void) {              // таймер + канал LEDC — це і є «tone» на ESP32
  ledc_timer_config_t t = {
    .speed_mode      = LEDC_LOW_SPEED_MODE,
    .duty_resolution = LEDC_TIMER_10_BIT,  // 0..1023, половина = меандр
    .timer_num       = LEDC_TIMER_0,
    .freq_hz         = NOTE_C5,            // частоту потім міняємо на льоту
    .clk_cfg         = LEDC_AUTO_CLK,
  };
  ESP_ERROR_CHECK(ledc_timer_config(&t));
  ledc_channel_config_t c = {
    .gpio_num = BUZ,           .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel  = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0,
    .duty     = 0,              .hpoint    = 0,
  };
  ESP_ERROR_CHECK(ledc_channel_config(&c));
}

static void play_note(uint32_t freq, uint32_t ms) {
  ledc_set_freq(LEDC_LOW_SPEED_MODE, LEDC_TIMER_0, freq);    // задали ноту
  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 512);   // 50 % — меандр
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
  vTaskDelay(pdMS_TO_TICKS(ms));                             // тримаємо ноту
  ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);     // тиша
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void app_main(void) {
  tone_init();
  while (1) {
    play_note(NOTE_C5, 200);               // до
    play_note(NOTE_E5, 200);               // мі
    play_note(NOTE_G5, 300);               // соль
    vTaskDelay(pdMS_TO_TICKS(1500));
  }
}
