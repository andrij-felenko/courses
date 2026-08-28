#include "esp_rom_sys.h"                    // esp_rom_delay_us()

// середній сирий відлік із N вимірів (шум давиться як √N)
static int read_raw_averaged(int samples) {
    uint32_t acc = 0;                       // 32 біти: 64×4095 не переповнить
    for (int i = 0; i < samples; i++) {
        int raw = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHAN, &raw));
        acc += (uint32_t)raw;
        esp_rom_delay_us(200);              // дати входу АЦП «устоятися»
    }
    return (int)(acc / samples);
}
