#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_oneshot.h"

// Коефіцієнт згладжування EMA (від 0.01 до 1.0)
#define EMA_ALPHA 0.15f
#define LM35_SENSITIVITY_V_PER_C 0.010f

void app_main(void) {
    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = ADC_UNIT_1,
    };
    adc_oneshot_new_unit(&init_config, &adc_handle);

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_12,
        .atten = ADC_ATTEN_DB_2_5, // Атенюація для діапазону шкали до ~1.1 V
    };
    adc_oneshot_config_channel(adc_handle, ADC_CHANNEL_0, &config);

    float filtered_temp = 0.0f;
    bool is_initialized = false;

    while (1) {
        int raw_adc = 0;
        adc_oneshot_read(adc_handle, ADC_CHANNEL_0, &raw_adc);

        // Перетворення коду 12-бітного АЦП у напругу при Vref = 1.100 V
        float voltage_v = ((float)raw_adc / 4095.0f) * 1.100f;
        float current_temp = voltage_v / LM35_SENSITIVITY_V_PER_C;

        if (!is_initialized) {
            filtered_temp = current_temp;
            is_initialized = true;
        } else {
            filtered_temp = (EMA_ALPHA * current_temp) + ((1.0f - EMA_ALPHA) * filtered_temp);
        }

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
