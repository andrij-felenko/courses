#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define AO_CHANNEL  ADC_CHANNEL_6          // GPIO34 = ADC1_CH6 — ADC1, щоб дружити з Wi-Fi
#define WINDOW_MS   50
#define ADC_MAX     4095                   // стеля 12-бітного АЦП ESP32 (0..4095)

static const char *TAG = "ky038";
static adc_oneshot_unit_handle_t adc1;
static int  center  = 2048;                // де стоїть центр сигналу (контроль країв)
static bool clipped = false;

static inline uint32_t millis_now(void) {
    return (uint32_t)(esp_timer_get_time() / 1000);
}

static int measure_amplitude(void) {
    int lo = ADC_MAX, hi = 0, v = 0;
    uint32_t t0 = millis_now();
    while (millis_now() - t0 < WINDOW_MS) {
        if (adc_oneshot_read(adc1, AO_CHANNEL, &v) != ESP_OK) continue;
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    center  = (hi + lo) / 2;
    clipped = (hi >= ADC_MAX) || (lo <= 0);
    return hi - lo;
}

static const char *loudness_level(int amp) {   // пороги під 12-бітну шкалу
    if (amp < 40)   return "тиша";
    if (amp < 150)  return "чутно";
    if (amp < 500)  return "голосно";
    return "дуже голосно";
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t ch = {
        .bitwidth = ADC_BITWIDTH_12,
        .atten    = ADC_ATTEN_DB_12,       // ОБОВ'ЯЗКОВО: діапазон до ~3.3 В
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, AO_CHANNEL, &ch));
    vTaskDelay(pdMS_TO_TICKS(300));        // дати мікрофону встановити зсув

    for (;;) {
        int amp = measure_amplitude();
        ESP_LOGI(TAG, "розмах = %4d  →  %s%s", amp, loudness_level(amp),
                 clipped ? "   [!] обрізання — постав гвинтик у середину" : "");
        vTaskDelay(pdMS_TO_TICKS(30));
    }
}
