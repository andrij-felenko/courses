// ESP-IDF 5.x: той самий конвеєр, АЦП — через драйвер adc_oneshot
#include <math.h>
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define ADC_CHAN   ADC_CHANNEL_6     // ADC1_CH6 = GPIO34, сигнал S давача
#define ADC_MAX    4095.0f           // 12-біт АЦП: повна шкала (2^12 − 1)
#define R_FIXED    10000.0f          // сталий резистор на модулі, Ом
#define R25        10000.0f          // опір термістора за 25 °C, Ом
#define BETA       3950.0f           // B-параметр термістора, K
#define T25_K      298.15f           // 25 °C у кельвінах

static const char *TAG = "ky013";
static adc_oneshot_unit_handle_t adc1;

// відлік АЦП → опір термістора (термістор у ВЕРХНЬОМУ плечі)
static float raw_to_resistance(int raw) {
    float ratio = (float)raw / ADC_MAX;          // U_S / Vcc, у межах 0..1
    return R_FIXED * (1.0f / ratio - 1.0f);      // R_ntc = R_fixed·(1/ratio − 1)
}

// опір термістора → температура, °C (B-параметр)
static float resistance_to_temp_c(float r_ntc) {
    float invT = 1.0f / T25_K + logf(r_ntc / R25) / BETA;
    return 1.0f / invT - 273.15f;                // K → °C
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t ch = {
        .bitwidth = ADC_BITWIDTH_12,             // 12 біт → шкала 0…4095
        .atten    = ADC_ATTEN_DB_12,             // повний вхідний діапазон
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHAN, &ch));

    while (1) {
        int raw = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHAN, &raw));
        float tempC = resistance_to_temp_c(raw_to_resistance(raw));
        ESP_LOGI(TAG, "%.1f C", tempC);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
