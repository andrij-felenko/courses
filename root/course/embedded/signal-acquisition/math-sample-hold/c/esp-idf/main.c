#include "esp_adc/adc_oneshot.h"     // ESP-IDF v5, ADC1, 12 біт
#include "esp_log.h"

static adc_oneshot_unit_handle_t adc1;   // ручка юніта, створена при старті

int read_clean(adc_channel_t ch, int n) {
    int raw = 0;
    adc_oneshot_read(adc1, ch, &raw);        // холостий: гасить хвіст старого каналу
    uint32_t acc = 0;                        // 32 біти: 16×4095 не переповнить
    for (int i = 0; i < n; ++i) {            // усереднення: шум ↓ як √n
        esp_err_t err = adc_oneshot_read(adc1, ch, &raw);
        if (err != ESP_OK) { ESP_LOGE("adc", "канал %d: %s", ch, esp_err_to_name(err)); return -1; }
        acc += (uint32_t)raw;
    }
    return (int)(acc / n);                   // середнє, 0..4095
}
