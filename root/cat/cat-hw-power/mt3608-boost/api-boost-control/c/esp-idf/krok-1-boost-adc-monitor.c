/* ============================================================================
   krok-1-boost-adc-monitor.c — ESP-IDF: моніторинг високої напруги MT3608
   ========================================================================== */

#include <stdio.h>
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

static const char *TAG = "MT3608_ADC";

#define ADC_CHANNEL_BOOST    ADC_CHANNEL_5    // GPIO33 на ESP32
#define DIVIDER_RATIO        11.0f            // (100 кОм + 10 кОм) / 10 кОм

static adc_oneshot_unit_handle_t s_adc_handle;
static adc_cali_handle_t         s_cali_handle;
static bool                      s_calibrated = false;

void mt3608_adc_init(void) {
    adc_oneshot_unit_init_cfg_t init_cfg = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_cfg, &s_adc_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .atten = ADC_ATTEN_DB_12,             // 0..3100 мВ
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc_handle, ADC_CHANNEL_BOOST, &chan_cfg));

    adc_cali_curve_fitting_config_t cali_cfg = {
        .unit_id = ADC_UNIT_1,
        .chan = ADC_CHANNEL_BOOST,
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    if (adc_cali_create_scheme_curve_fitting(&cali_cfg, &s_cali_handle) == ESP_OK) {
        s_calibrated = true;
    }
}

uint32_t mt3608_get_voltage_mv(void) {
    int raw = 0;
    int pin_mv = 0;

    for (int i = 0; i < 8; ++i) {
        int sample = 0;
        adc_oneshot_read(s_adc_handle, ADC_CHANNEL_BOOST, &sample);
        raw += sample;
    }
    raw /= 8;

    if (s_calibrated) {
        adc_cali_raw_to_voltage(s_cali_handle, raw, &pin_mv);
    } else {
        pin_mv = (raw * 3100) / 4095;
    }

    uint32_t vout_mv = (uint32_t)(pin_mv * DIVIDER_RATIO);
    return vout_mv;
}
