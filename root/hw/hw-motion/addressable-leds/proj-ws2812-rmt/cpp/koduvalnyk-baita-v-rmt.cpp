#include <driver/rmt.h>          // Arduino ESP32 core 3.x
// rmtInit(pin, RMT_TX_MODE, RMT_MEM_NUM_BLOCKS_1, 10000000)
// → tick = 1/10MHz = 100 нс = 0.1 мкс

// Тривалості у тіках (tick = 0.1 мкс) — за специфікацією WS2812B
#define T0H  4    // 0.4 мкс HIGH для «0»
#define T0L  9    // 0.85 мкс LOW  для «0» (9 × 0.1 ≈ 0.9, у допуску)
#define T1H  8    // 0.8 мкс HIGH для «1»
#define T1L  5    // 0.45 мкс LOW  для «1» (5 × 0.1 = 0.5, у допуску)

// Кодує один байт у 8 RMT-символів; out — масив на 8 елементів
void encodeByte(uint8_t b, rmt_data_t* out) {
    for (int i = 0; i < 8; i++) {
        int bit = (b >> (7 - i)) & 1;   // старший біт першим (MSB-first)
        if (bit) {
            out[i].level0    = 1;
            out[i].duration0 = T1H;
            out[i].level1    = 0;
            out[i].duration1 = T1L;
        } else {
            out[i].level0    = 1;
            out[i].duration0 = T0H;
            out[i].level1    = 0;
            out[i].duration1 = T0L;
        }
    }
}
