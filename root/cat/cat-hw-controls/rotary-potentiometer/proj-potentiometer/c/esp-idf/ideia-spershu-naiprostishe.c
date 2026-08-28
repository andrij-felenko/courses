#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"

static const char *TAG = "pot";
#define POT_CHAN  ADC_CHANNEL_6           // ADC1_CH6 — це GPIO34
#define ADC_MAX   4095                    // 12 біт

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };   // ADC1: не свариться з Wi-Fi
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));

  adc_oneshot_chan_cfg_t ch = {
    .atten    = ADC_ATTEN_DB_12,          // вхід ≈0..3.3 В (у старих IDF — DB_11)
    .bitwidth = ADC_BITWIDTH_DEFAULT,     // 12 біт: 0..4095
  };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, POT_CHAN, &ch));

  while (1) {
    int raw = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, POT_CHAN, &raw));   // 0..4095: сира частка ходу
    int pct = raw * 100 / ADC_MAX;        // та сама пропорція, тільки руками
    ESP_LOGI(TAG, "%d  ->  %d %%", raw, pct);
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}
