#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"

#define LM35_ADC_CHANNEL    ADC_CHANNEL_6
#define FILTER_ALPHA        0.1f

static const char *TAG = "LM35_DRIVER";

float read_lm35_temperature_c(adc_oneshot_unit_handle_t adc_handle) {
    static float filtered_raw = 0.0f;
    int raw_adc = 0;
    
    if (adc_oneshot_read(adc_handle, LM35_ADC_CHANNEL, &raw_adc) == ESP_OK) {
        if (filtered_raw == 0.0f) {
            filtered_raw = (float)raw_adc;
        } else {
            filtered_raw = FILTER_ALPHA * (float)raw_adc + (1.0f - FILTER_ALPHA) * filtered_raw;
        }
        // Розрахунок напруги для 12-бітного АЦП при опорній напрузі 1100 мВ
        float voltage_mv = (filtered_raw / 4095.0f) * 1100.0f;
        float temperature_c = voltage_mv / 10.0f; // 10 мВ/°C
        return temperature_c;
    }
    ESP_LOGE(TAG, "Помилка зчитування АЦП");
    return -273.15f;
}
