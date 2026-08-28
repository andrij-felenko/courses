#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

adc_cali_handle_t cali;
adc_cali_line_fitting_config_t cfg = {
  .unit_id  = ADC_UNIT_1,
  .atten    = ADC_ATTEN_DB_12,
  .bitwidth = ADC_BITWIDTH_12,
};
ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&cfg, &cali));

int raw = 0, mv = 0;
ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHANNEL_6, &raw));
ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, raw, &mv));   // калібровані мілівольти
