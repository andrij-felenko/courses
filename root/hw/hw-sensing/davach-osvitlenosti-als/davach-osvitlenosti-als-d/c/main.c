#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t gain_idx;      /* 0: 1x, 1: 4x, 2: 16x, 3: 128x */
    uint8_t tint_idx;      /* 0: 50ms, 1: 100ms, 2: 400ms */
    float glass_factor;    /* Коефіцієнт скла K_glass */
} als_state_t;

static const float GAINS[4] = {1.0f, 4.0f, 16.0f, 128.0f};
static const float TINTS[3] = {0.5f, 1.0f, 4.0f};

/* Адаптивне оновлення підсилення з гістерезисом */
bool als_update_range(als_state_t *st, uint16_t ch0_raw, bool overflow) {
    bool reconfigure = false;
    if (overflow || ch0_raw > 55705) { /* > 85% від 65535 */
        if (st->gain_idx > 0) {
            st->gain_idx--;
            reconfigure = true;
        } else if (st->tint_idx > 0) {
            st->tint_idx--;
            reconfigure = true;
        }
    } else if (ch0_raw < 6553) {       /* < 10% від 65535 */
        if (st->gain_idx < 3) {
            st->gain_idx++;
            reconfigure = true;
        } else if (st->tint_idx < 2) {
            st->tint_idx++;
            reconfigure = true;
        }
    }
    return reconfigure;
}

/* Обчислення абсолютних люксів */
float als_get_lux(const als_state_t *st, uint16_t ch0, uint16_t ch1) {
    if (ch0 == 0) return 0.0f;
    float ratio = (float)ch1 / (float)ch0;
    float a = 1.0f, b = 1.8f;
    if (ratio <= 0.20f) { a = 1.0f; b = 0.5f; }
    else if (ratio <= 0.60f) { a = 1.0f; b = 1.3f; }
    
    float net = a * (float)ch0 - b * (float)ch1;
    if (net < 0.0f) net = 0.0f;
    
    float lsb = (0.096f / (GAINS[st->gain_idx] * TINTS[st->tint_idx])) * st->glass_factor;
    return net * lsb;
}
