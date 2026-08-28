#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

#define POT_CHANNEL  ADC_CHANNEL_3   // IO3 = канал 3 на ADC1

static adc_oneshot_unit_handle_t adc1;
static adc_cali_handle_t cali;

static void adc_init(void)
{
    adc_oneshot_unit_init_cfg_t unit_cfg = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit_cfg, &adc1));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .atten = ADC_ATTEN_DB_12,        // діапазон до ~3.3 В
        .bitwidth = ADC_BITWIDTH_12,     // 0..4095
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, POT_CHANNEL, &chan_cfg));

    // калібрування «крива-припасування» (curve fitting) для C6
    adc_cali_curve_fitting_config_t cali_cfg = {
        .unit_id = ADC_UNIT_1,
        .chan = POT_CHANNEL,
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_12,
    };
    ESP_ERROR_CHECK(adc_cali_create_scheme_curve_fitting(&cali_cfg, &cali));
}

void app_main(void)
{
    adc_init();
    while (1) {
        int raw = 0, mv = 0;
        adc_oneshot_read(adc1, POT_CHANNEL, &raw);      // 0..4095
        adc_cali_raw_to_voltage(cali, raw, &mv);        // → мілівольти
        printf("raw=%d  U=%d мВ\n", raw, mv);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
