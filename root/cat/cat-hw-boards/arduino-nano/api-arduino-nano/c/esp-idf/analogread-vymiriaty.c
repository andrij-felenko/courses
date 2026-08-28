#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "adc";

void app_main(void) {
    adc_oneshot_unit_handle_t adc1;
    const adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));

    const adc_oneshot_chan_cfg_t ch = {
        .bitwidth = ADC_BITWIDTH_12,     // 12 бітів: 0..4095
        .atten    = ADC_ATTEN_DB_12,     // послаблення входу — стеля близько 3.3 В
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_0, &ch));

    while (1) {
        int raw = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHANNEL_0, &raw));
        float volts = raw * 3.3f / 4095.0f;         // назад у вольти
        ESP_LOGI(TAG, "%d  ->  %.3f В", raw, volts);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
