#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"
#include "esp_log.h"

#define MIC_CHAN   ADC_CHANNEL_6         // ADC1_CH6 = GPIO34 — блок АЦП1, дружній до Wi-Fi
#define WINDOW_US  50000                 // вікно вимірювання, 50 мс

static adc_oneshot_unit_handle_t adc1;

static void mic_begin(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t chan = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,   // 12 біт → 0…4095
        .atten    = ADC_ATTEN_DB_12,        // повний вхідний діапазон
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, MIC_CHAN, &chan));
}

static int measure_peak_to_peak(void) {
    int64_t t0 = esp_timer_get_time();
    int hi = 0, lo = 4095, v;             // межі 12-бітного АЦП ESP32
    while (esp_timer_get_time() - t0 < WINDOW_US) {
        adc_oneshot_read(adc1, MIC_CHAN, &v);   // миттєва точка хвилі
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    return hi - lo;                       // РОЗМАХ: тиша ≈ мало, гучно ≈ багато
}

void app_main(void) {
    mic_begin();
    while (1) ESP_LOGI("ky037", "%d", measure_peak_to_peak());
}
