// Те саме на драйвері adc_oneshot: холостий + усереднення.
// N обираємо з потрібної чистоти: треба σ/√N ≤ ціль  →  N ≥ (σ/ціль)².
#include "esp_adc/adc_oneshot.h"

static uint32_t read_clean(adc_oneshot_unit_handle_t adc, adc_channel_t ch, int n) {
    int raw = 0;
    adc_oneshot_read(adc, ch, &raw);          // холостий після перемикання — відкидаємо
    uint32_t acc = 0;                         // 32 біти: 256×4095 = 1 048 320 не переповнить
    for (int i = 0; i < n; ++i) {
        ESP_ERROR_CHECK(adc_oneshot_read(adc, ch, &raw));
        acc += (uint32_t)raw;
    }
    return acc / (uint32_t)n;                 // середнє, 0..4095
}
