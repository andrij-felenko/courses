#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define WIN_US 50000LL                        // вікно вимірювання: 50 мс у мкс
#define AO_CH  ADC_CHANNEL_6                  // ADC1 канал 6 = GPIO34

static const char *TAG = "sound";
static adc_oneshot_unit_handle_t adc1;

static void adc_setup(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };  // ADC1 живе з Wi-Fi
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t chan = {
        .atten    = ADC_ATTEN_DB_12,          // повна шкала ~0.15…3.1 В
        .bitwidth = ADC_BITWIDTH_DEFAULT,     // 12 біт → 0…4095
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, AO_CH, &chan));
}

static int measure_peak_to_peak(void) {
    int64_t start = esp_timer_get_time();
    int lo = 4095, hi = 0, v = 0;
    while (esp_timer_get_time() - start < WIN_US) {
        if (adc_oneshot_read(adc1, AO_CH, &v) != ESP_OK) continue;
        if (v < lo) lo = v;
        if (v > hi) hi = v;
    }
    return hi - lo;
}

void app_main(void) {
    adc_setup();
    while (1) {
        int amp = measure_peak_to_peak();
        ESP_LOGI(TAG, "розмах: %d%s", amp, amp > 250 ? "  → гучно!" : "");
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
