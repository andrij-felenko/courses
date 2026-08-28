#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

static const char *TAG = "pot";

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_6, &ch));

  adc_cali_handle_t cali = NULL;            // класичний ESP32 — схема line fitting
  adc_cali_line_fitting_config_t cfg = {
    .unit_id = ADC_UNIT_1, .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT,
  };
  ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&cfg, &cali));

  while (1) {
    int raw = 0, mv = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHANNEL_6, &raw));
    ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, raw, &mv));   // мВ, уже виправлені
    ESP_LOGI(TAG, "%d мВ", mv);
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}
