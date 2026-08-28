// Той самий цикл задачею FreeRTOS: чекаємо знак таймера — і лише тоді працюємо.
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

#define ADC_CH  ADC_CHANNEL_6            // ADC1_CH6 = GPIO34 — стабільний за Wi-Fi
#define N_AVG   16                       // √16 = 4× тихіше; +2 «ефективні» біти

void sampler_task(void* arg) {
    adc_oneshot_unit_handle_t adc;
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc));
    adc_oneshot_chan_cfg_t chan = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, ADC_CH, &chan));

    adc_cali_handle_t cali;              // заводські коефіцієнти: зсув + нелінійність
    adc_cali_line_fitting_config_t cc = { .unit_id = ADC_UNIT_1,
        .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
    ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&cc, &cali));

    setup_sampler(1000);                 // fs = 1 кГц: надвибірка над повільним давачем

    for (;;) {
        xSemaphoreTake(tick, portMAX_DELAY);   // поки не час знімка — задача спить
        uint32_t code = read_clean(adc, ADC_CH, N_AVG);   // чисте усереднене читання
        int mv = 0;
        ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, (int)code, &mv));   // калібровані мВ
        control_step(mv);                // готове число — регулятору (наступний крок модуля)
    }
}
