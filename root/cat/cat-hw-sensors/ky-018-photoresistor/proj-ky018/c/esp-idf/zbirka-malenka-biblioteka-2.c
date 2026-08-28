#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "ldr";
static light_sensor_t sensor;

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };   // ADC1 — не свариться з Wi-Fi
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_6, &ch));  // GPIO34

  gpio_config_t io = { .pin_bit_mask = 1ULL << GPIO_NUM_2, .mode = GPIO_MODE_OUTPUT };
  ESP_ERROR_CHECK(gpio_config(&io));

  light_begin(&sensor, adc1, ADC_CHANNEL_6, 4095, 0.2f, 30, 45);  // 12-бітний АЦП
  ESP_LOGI(TAG, "Калібрування: 5 с крутіть освітлення...");
  light_calibrate(&sensor, 5);

  for (;;) {
    light_update(&sensor);              // оновити фільтр
    uint8_t pct = light_percent(&sensor);
    bool dark = light_is_dark(&sensor);
    gpio_set_level(GPIO_NUM_2, dark);   // світлодіод плати в темряві
    ESP_LOGI(TAG, "яскравість %u %%  %s", pct, dark ? "ТЕМНО" : "світло");
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
