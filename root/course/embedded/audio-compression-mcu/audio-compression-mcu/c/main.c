#include <stdint.h>

// Стан живе МІЖ відліками, тому статичний: як і у кодера, декодер
// пам'ятає свою оцінку сигналу й поточний крок квантування.
static int32_t predict = 0;   // передбачений (попередній відновлений) відлік
static int32_t step    = 7;   // поточний розмір сходинки квантування

int16_t adpcm_decode_nibble(uint8_t code) {
    // 3 молодші біти — величина, старший — знак
    int32_t diff = step >> 3;                 // базовий внесок (половина сходинки)
    if (code & 4) diff += step;               // біт «×1»
    if (code & 2) diff += step >> 1;          // біт «×1/2»
    if (code & 1) diff += step >> 2;          // біт «×1/4»
    if (code & 8) predict -= diff;            // знак: віднімаємо або додаємо
    else          predict += diff;

    // не даємо відліку вийти за 16-бітний діапазон
    if (predict >  32767) predict =  32767;
    if (predict < -32768) predict = -32768;

    step = adpcm_next_step(step, code);       // крок адаптується (таблиця, див. нижче)
    return (int16_t)predict;
}
