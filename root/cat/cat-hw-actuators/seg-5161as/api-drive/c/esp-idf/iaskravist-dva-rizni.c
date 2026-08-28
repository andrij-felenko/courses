#include "driver/ledc.h"

// Спільний катод заведено на вивід МК (через транзистор, якщо струм великий).
// Шпаруватість тримає периферія LEDC — ядро в цьому не бере участі зовсім.
#define COM_PIN  GPIO_NUM_10

static void brightness_begin(void) {
  ledc_timer_config_t t = {
    .speed_mode      = LEDC_LOW_SPEED_MODE,
    .duty_resolution = LEDC_TIMER_8_BIT,   // шпаруватість 0..255
    .timer_num       = LEDC_TIMER_0,
    .freq_hz         = 1000,               // 1 кГц — око мерехтіння не бачить
    .clk_cfg         = LEDC_AUTO_CLK,
  };
  ESP_ERROR_CHECK(ledc_timer_config(&t));
  ledc_channel_config_t c = {
    .gpio_num   = COM_PIN,
    .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel    = LEDC_CHANNEL_0,
    .timer_sel  = LEDC_TIMER_0,
    .duty       = 255,                     // старт із погашеного
    .hpoint     = 0,
  };
  ESP_ERROR_CHECK(ledc_channel_config(&c));
}

// Катод світить НИЗЬКИМ рівнем → яскравість = час, коли вихід унизу.
static void set_brightness(uint8_t b) {
  ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 255 - b));
  ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0));
}

void app_main(void) {
  seg_begin();
  brightness_begin();
  seg_show_hex(0x3, false);          // показуємо «3»
  set_brightness(128);               // половина яскравості
  while (true) vTaskDelay(pdMS_TO_TICKS(1000));   // ядро вільне
}
