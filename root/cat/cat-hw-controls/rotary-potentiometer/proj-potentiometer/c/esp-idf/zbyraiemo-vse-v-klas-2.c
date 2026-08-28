#include "driver/ledc.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "pot";
#define POT_CHAN  ADC_CHANNEL_6           // GPIO34 (ADC1)
#define LED_GPIO  2                       // ШІМ-вихід під світлодіод

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, POT_CHAN, &ch));

  ledc_timer_config_t t = {                    // 8 біт заповнення → рівно 0..255
    .speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_8_BIT,
    .timer_num = LEDC_TIMER_0, .freq_hz = 5000, .clk_cfg = LEDC_AUTO_CLK,
  };
  ESP_ERROR_CHECK(ledc_timer_config(&t));
  ledc_channel_config_t c = {
    .gpio_num = LED_GPIO, .speed_mode = LEDC_LOW_SPEED_MODE, .channel = LEDC_CHANNEL_0,
    .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0,
  };
  ESP_ERROR_CHECK(ledc_channel_config(&c));

  pot_t pot;
  pot_begin(&pot, adc1, POT_CHAN, 4, 16);      // SHIFT=4, мертва зона 16 (12 біт!)

  // 3-секундне калібрування: крути ручку від упору до упору.
  ESP_LOGI(TAG, "Калібрування: крути ручку від краю до краю...");
  for (int i = 0; i < 600; i++) { pot_calibrate(&pot); vTaskDelay(pdMS_TO_TICKS(5)); }
  ESP_LOGI(TAG, "Готово.");

  while (1) {
    int bright;
    // яскравість 0..255; подія лише коли ручку реально крутнули
    if (pot_changed(&pot, &bright, 0, 255)) {
      ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, bright);
      ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
      ESP_LOGI(TAG, "яскравість = %d", bright);
    }
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
