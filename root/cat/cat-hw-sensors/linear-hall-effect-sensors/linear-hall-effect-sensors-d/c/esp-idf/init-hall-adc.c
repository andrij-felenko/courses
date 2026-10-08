#include <stdio.h>
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define HALL_ADC_UNIT       ADC_UNIT_1
#define HALL_ADC_CHANNEL    ADC_CHANNEL_6 // GPIO34
#define ADC_ATTEN           ADC_ATTEN_DB_12 // Full scale 0-3.3V
#define EMA_ALPHA           0.15f // Smoothing factor (0.0 to 1.0)

static adc_oneshot_unit_handle_t adc_handle;
static float filtered_adc_code = 2048.0f; // Initial midpoint for 12-bit ADC

void init_hall_adc(void) {
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = HALL_ADC_UNIT,
    };
    adc_oneshot_new_unit(&init_config, &adc_handle);

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN,
    };
    adc_oneshot_config_channel(adc_handle, HALL_ADC_CHANNEL, &config);
}

float read_filtered_hall_adc(void) {
    int raw_val = 0;
    adc_oneshot_read(adc_handle, HALL_ADC_CHANNEL, &raw_val);
    
    // Exponential Moving Average (EMA) filter
    filtered_adc_code = (EMA_ALPHA * (float)raw_val) + ((1.0f - EMA_ALPHA) * filtered_adc_code);
    return filtered_adc_code;
}

void app_main(void) {
    init_hall_adc();
    while (1) {
        float adc_val = read_filtered_hall_adc();
        // Convert to voltage assuming ratiometric VCC reference
        float voltage_mv = (adc_val / 4095.0f) * 3300.0f;
        printf("ADC Code: %.1f | Voltage: %.2f mV\n", adc_val, voltage_mv);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
