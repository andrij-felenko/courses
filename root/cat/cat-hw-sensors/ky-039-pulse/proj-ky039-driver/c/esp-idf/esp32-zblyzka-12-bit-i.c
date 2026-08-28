// ── Те саме рідним SDK: блок АЦП і ширину задаємо явно, тракт не міняється ──

#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PULSE_CH   ADC_CHANNEL_6     // GPIO34 — АЦП1; на АЦП2 Wi-Fi зламав би читання
#define SAMPLE_US  20000             // 50 Гц

static adc_oneshot_unit_handle_t s_adc;

static void adc_setup(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };   // САМЕ АЦП1
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &s_adc));

    adc_oneshot_chan_cfg_t chan = {
        .atten    = ADC_ATTEN_DB_12,     // повний розмах входу
        .bitwidth = ADC_BITWIDTH_12,     // 12 біт → 0..4095, звідси MIN_AMP ×4
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc, PULSE_CH, &chan));
}

static void pulse_task(void *arg) {
    int raw = 0;
    adc_oneshot_read(s_adc, PULSE_CH, &raw);
    g_baseline = raw;                            // старт нуля з першого відліку
    int64_t last = esp_timer_get_time();

    while (1) {
        int64_t now = esp_timer_get_time();
        if (now - last < SAMPLE_US) { vTaskDelay(1); continue; }
        last += SAMPLE_US;                       // рівна сітка, не «= now»

        adc_oneshot_read(s_adc, PULSE_CH, &raw); // 0..4095
        process(raw, now / 1000);                // нуль, згладжування, піки, BPM — без змін
    }
}

void app_main(void) {
    adc_setup();
    xTaskCreate(pulse_task, "pulse", 4096, NULL, 5, NULL);
}
