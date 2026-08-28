// ESP-IDF v5 (ESP32) — рейка 5 В, АЦП 3.3-вольтового класу.
// На 12 дБ послаблення верх лінійності ~2.45 В, тож ділимо СИЛЬНІШЕ:
// R1=15к, R2=10к → k=0.4 → 5.2 В рейки дають 2.08 В у вузлі (у лінійній зоні).
// Мілівольти беремо з КАЛІБРУВАННЯ (враховує розкид опори 1000..1200 мВ).
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "rail";
#define R1 15000.0f
#define R2 10000.0f
#define DIV  ((R1 + R2) / R2)      // = 2.5, обернений коефіцієнт
#define BROWNOUT_MV 4600           // поріг у мілівольтах рейки

void app_main(void) {
    // 1) канал АЦП: GPIO34 = ADC1_CHANNEL_6 на класичному ESP32
    adc_oneshot_unit_handle_t adc;
    adc_oneshot_unit_init_cfg_t ucfg = { .unit_id = ADC_UNIT_1 };
    adc_oneshot_new_unit(&ucfg, &adc);

    adc_oneshot_chan_cfg_t ccfg = {
        .atten = ADC_ATTEN_DB_12,          // ~0..3.3 В (кол. DB_11)
        .bitwidth = ADC_BITWIDTH_DEFAULT,  // зазвичай 12 біт
    };
    adc_oneshot_config_channel(adc, ADC_CHANNEL_6, &ccfg);

    // 2) калібрування — воно й дає ЧЕСНІ мілівольти попри розкид опори
    adc_cali_handle_t cali = NULL;
    adc_cali_curve_fitting_config_t kcfg = {
        .unit_id  = ADC_UNIT_1,
        .atten    = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    adc_cali_create_scheme_curve_fitting(&kcfg, &cali);

    while (1) {
        int raw, mv, acc = 0;
        for (int i = 0; i < 8; i++) {          // усереднення від шуму
            adc_oneshot_read(adc, ADC_CHANNEL_6, &raw);
            adc_cali_raw_to_voltage(cali, raw, &mv);
            acc += mv;
        }
        int node = acc / 8;                     // мілівольти у вузлі (середнє)
        int rail = (int)(node * DIV);           // назад у мілівольти рейки

        if (rail < BROWNOUT_MV)
            ESP_LOGW(TAG, "BROWNOUT! рейка = %d мВ", rail);
        else
            ESP_LOGI(TAG, "рейка OK: %d мВ", rail);

        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
