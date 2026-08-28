// На ESP32 flash відображена в адресний простір: таблиця — звичайний
// static const, читається прямо, без PROGMEM і pgm_read_word.
#include <stdlib.h>
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct { int16_t adc; int16_t t10; } point_t;

// «відлік АЦП → температура×10 (десяті °C)», шкала 12-бітна (0…4095).
// Термістор УНИЗУ (між S і −): гарячіше → напруга на S нижча → відлік менший.
static const point_t TABLE[] = {
    {3495, -100}, {3338,  -50}, {3154,    0}, {2954,   50},
    {2738,  100}, {2510,  150}, {2278,  200}, {2050,  250},
    {1825,  300}, {1613,  350}, {1417,  400}, {1241,  450},
};
#define N  (sizeof(TABLE) / sizeof(TABLE[0]))

// відлік → температура×10, лінійна інтерполяція по таблиці (без float!)
static int16_t lookup_t10(int16_t raw) {
    if (raw >= TABLE[0].adc)     return TABLE[0].t10;      // за краєм — обрізаємо
    if (raw <= TABLE[N - 1].adc) return TABLE[N - 1].t10;

    for (size_t i = 0; i < N - 1; i++) {
        int16_t aHi = TABLE[i].adc;          // більший відлік
        int16_t aLo = TABLE[i + 1].adc;      // менший відлік
        if (raw <= aHi && raw >= aLo) {
            int16_t tHi = TABLE[i].t10, tLo = TABLE[i + 1].t10;
            // t = tHi + (tLo − tHi)·(aHi − raw)/(aHi − aLo), уся арифметика ціла
            int32_t num = (int32_t)(tLo - tHi) * (aHi - raw);
            return tHi + (int16_t)(num / (aHi - aLo));
        }
    }
    return TABLE[N - 1].t10;                 // сюди не дійде, для повноти
}

void app_main(void) {
    /* ініціалізація adc_oneshot — та сама, що в першому прикладі */
    while (1) {
        int raw = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHAN, &raw));
        int16_t t10 = lookup_t10((int16_t)raw);
        ESP_LOGI(TAG, "%d.%d C", t10 / 10, abs(t10 % 10));
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
