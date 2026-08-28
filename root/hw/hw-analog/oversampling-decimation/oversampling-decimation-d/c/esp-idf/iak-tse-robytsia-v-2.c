#include "esp_adc/adc_oneshot.h"

// Передискретизація з децимацією: 16 знімків → один 14-бітний результат.
// Сума ділиться на √16 = 4, а не на 16 — так зберігаються 2 додаткові біти.
//   ×4 знімків = +1 біт  →  ×16 = +2 біти  →  ділимо на 2² = 4.
esp_err_t oversample_14bit(adc_oneshot_unit_handle_t adc, adc_channel_t ch, uint16_t *out) {
    uint32_t acc = 0;
    int raw = 0;
    for (int i = 0; i < 16; i++) {
        esp_err_t err = adc_oneshot_read(adc, ch, &raw);  // 12-бітні знімки (0..4095)
        if (err != ESP_OK) return err;
        acc += (uint32_t)raw;
    }
    *out = (uint16_t)(acc >> 2);    // ÷4: результат уже 14-бітний (0..16380)
    return ESP_OK;
}
