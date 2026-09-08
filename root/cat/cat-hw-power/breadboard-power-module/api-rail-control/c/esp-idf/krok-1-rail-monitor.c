/* ============================================================================
   krok-1-rail-monitor.c — ESP-IDF: моніторинг шини MB102 з калібруванням АЦП
   ========================================================================== */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

static const char *TAG = "MB102_MONITOR";

#define ADC_CHANNEL_RAIL     ADC_CHANNEL_4    // GPIO32 на ESP32
#define DIVIDER_RATIO        3.0f             // Дільник (20 кОм + 10 кОм) / 10 кОм

static adc_oneshot_unit_handle_t s_adc_handle;
static adc_cali_handle_t         s_cali_handle;
static bool                      s_calibrated = false;

static void init_adc(void) {
    adc_oneshot_unit_init_cfg_t init_cfg = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_cfg, &s_adc_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .atten = ADC_ATTEN_DB_12,             // Діапазон до ~3.1 В
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc_handle, ADC_CHANNEL_RAIL, &chan_cfg));

    // Калібрування АЦП (лінеаризація за eFuse)
    adc_cali_curve_fitting_config_t cali_cfg = {
        .unit_id = ADC_UNIT_1,
        .chan = ADC_CHANNEL_RAIL,
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    if (adc_cali_create_scheme_curve_fitting(&cali_cfg, &s_cali_handle) == ESP_OK) {
        s_calibrated = true;
    }
}

uint32_t read_rail_mv(void) {
    int raw = 0;
    int voltage_pin_mv = 0;

    // Усереднення 8 вибірок
    for (int i = 0; i < 8; ++i) {
        int sample = 0;
        adc_oneshot_read(s_adc_handle, ADC_CHANNEL_RAIL, &sample);
        raw += sample;
    }
    raw /= 8;

    if (s_calibrated) {
        adc_cali_raw_to_voltage(s_cali_handle, raw, &voltage_pin_mv);
    } else {
        voltage_pin_mv = (raw * 3100) / 4095;
    }

    uint32_t rail_mv = (uint32_t)(voltage_pin_mv * DIVIDER_RATIO);
    return rail_mv;
}

void app_main(void) {
    ESP_LOGI(TAG, "Ініціалізація супервізора шини MB102...");
    init_adc();

    while (1) {
        uint32_t mv = read_rail_mv();
        ESP_LOGI(TAG, "Шина MB102: %lu мВ", mv);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
