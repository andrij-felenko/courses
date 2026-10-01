// Перевірка стану живлення та ініціалізація ADC для моніторингу VDD
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"

#define POWER_MONITOR_ADC_CHANNEL ADC_CHANNEL_0 // GPIO1

void check_power_rails(void) {
    adc_oneshot_unit_handle_t adc1_handle;
    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config1, &adc1_handle));

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, POWER_MONITOR_ADC_CHANNEL, &config));

    int raw_val = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, POWER_MONITOR_ADC_CHANNEL, &raw_val));
    ESP_LOGI("PWR", "Системний рівень напруги ADC raw: %d", raw_val);
}
