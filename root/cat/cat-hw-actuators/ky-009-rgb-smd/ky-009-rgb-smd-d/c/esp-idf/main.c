// KY-009, спільний катод. R→GPIO25, G→GPIO26, B→GPIO27 (кожен ЧЕРЕЗ резистор); − → GND.
#include "driver/ledc.h"

#define RGB_MODE LEDC_LOW_SPEED_MODE
static const int rgb_gpio[3] = { 25, 26, 27 };

static void rgb_init(void) {
  ledc_timer_config_t tcfg = {
    .speed_mode      = RGB_MODE,
    .timer_num       = LEDC_TIMER_0,
    .duty_resolution = LEDC_TIMER_8_BIT,   // шпаруватість 0…255
    .freq_hz         = 1000,               // 1 кГц — око миготіння не бачить
    .clk_cfg         = LEDC_AUTO_CLK,
  };
  ESP_ERROR_CHECK(ledc_timer_config(&tcfg));

  for (int i = 0; i < 3; i++) {            // три канали на одному таймері
    ledc_channel_config_t ccfg = {
      .gpio_num   = rgb_gpio[i],
      .speed_mode = RGB_MODE,
      .channel    = (ledc_channel_t)(LEDC_CHANNEL_0 + i),
      .timer_sel  = LEDC_TIMER_0,
      .duty       = 0,
      .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ccfg));
  }
}

static void rgb_set(uint32_t r, uint32_t g, uint32_t b) {
  const uint32_t duty[3] = { r, g, b };    // спільний катод → більше = яскравіше
  for (int i = 0; i < 3; i++) {
    ledc_channel_t ch = (ledc_channel_t)(LEDC_CHANNEL_0 + i);
    ESP_ERROR_CHECK(ledc_set_duty(RGB_MODE, ch, duty[i]));
    ESP_ERROR_CHECK(ledc_update_duty(RGB_MODE, ch));   // нова шпаруватість діє лише після update
  }
}

void app_main(void) {
  rgb_init();
  rgb_set(255, 128, 0);                    // помаранчевий
}
