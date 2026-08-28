// DO на GPIO4, AO на GPIO34 (ADC1_CH6 — блок, дружній до Wi-Fi).
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "ky026";

static ky026_t sensor = {
    .pin_do = GPIO_NUM_4, .ch_ao = ADC_CHANNEL_6,
    .inverted = true, .debounce_us = 40 * 1000,
};

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &sensor.adc));
    ky026_begin(&sensor);

    for (;;) {                                  // це і є loop(), лише свій власний
        bool flame = ky026_update(&sensor);     // стабільний стан, без дрижання
        int  ir    = ky026_strength(&sensor);   // сира сила жару, якщо треба
        ESP_LOGI(TAG, "%s  %d", flame ? "ВОГОНЬ" : "спокій", ir);
        vTaskDelay(pdMS_TO_TICKS(10));          // update() любить часті виклики
    }
}
