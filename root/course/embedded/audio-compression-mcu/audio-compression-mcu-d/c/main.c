#include <stdint.h>

// Один спільний хелпер відновлення — ФІЗИЧНО той самий для кодера й декодера.
// Саме ця тотожність гарантує синхронність: розсинхронити копії правкою
// неможливо, бо копія одна.
static inline int32_t adpcm_reconstruct(int32_t step, uint8_t code) {
    int32_t vpdiff = step >> 3;              // базовий внесок = step/8
    if (code & 4) vpdiff += step;            // біт «×1»
    if (code & 2) vpdiff += step >> 1;       // біт «×1/2»
    if (code & 1) vpdiff += step >> 2;       // біт «×1/4»
    return (code & 8) ? -vpdiff : vpdiff;    // знак — старший біт коду
}

static uint8_t adpcm_encode_sample(int32_t *predict, int32_t *index, int16_t sample) {
    extern const int16_t step_table[89];
    extern const int8_t  index_table[16];
    int32_t step = step_table[*index];
    int32_t diff = (int32_t)sample - *predict;   // різниця з ВІДНОВЛЕНИМ передбаченням

    // --- КВАНТУВАННЯ: вибір коду відніманням порогів (це НЕ оновлення стану) ---
    uint8_t code = 0;
    if (diff < 0) { code = 8; diff = -diff; }
    int32_t t = step;
    if (diff >= t) { code |= 4; diff -= t; }
    t >>= 1;
    if (diff >= t) { code |= 2; diff -= t; }
    t >>= 1;
    if (diff >= t) { code |= 1; }

    // --- ВІДНОВЛЕННЯ: оновлюємо predict тим самим числом, що й декодер ---
    *predict += adpcm_reconstruct(step, code);   // САМЕ формулою декодера!
    if (*predict >  32767) *predict =  32767;     // обрізаємо однаково з обох боків
    if (*predict < -32768) *predict = -32768;

    *index += index_table[code];                  // крок за СТАРИМ індексом, зсув ПІСЛЯ
    if (*index < 0)  *index = 0;
    if (*index > 88) *index = 88;
    return code & 0x0f;
}
