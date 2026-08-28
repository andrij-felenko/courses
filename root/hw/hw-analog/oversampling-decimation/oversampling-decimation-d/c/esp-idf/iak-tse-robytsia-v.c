#include "esp_adc/adc_oneshot.h"

// Просте усереднення 16 знімків — повертає те саме 12-бітне число, лише чистіше.
uint16_t read_avg16(adc_oneshot_unit_handle_t adc, adc_channel_t ch) {
    uint32_t acc = 0;
    int raw = 0;
    for (int i = 0; i < 16; i++) {
        ESP_ERROR_CHECK(adc_oneshot_read(adc, ch, &raw));  // 16 знімків того самого каналу
        acc += (uint32_t)raw;
    }
    return (uint16_t)(acc / 16);    // середнє — у тому самому масштабі 0..4095
}
