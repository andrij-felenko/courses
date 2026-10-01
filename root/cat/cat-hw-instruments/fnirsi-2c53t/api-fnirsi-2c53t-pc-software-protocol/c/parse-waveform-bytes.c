#include <stdint.h>

// Структура налаштувань каналу осцилографа
typedef struct {
    float v_scale;   // Ціна розряду АЦП у вольтах
    float v_offset;  // Зміщення осі у вольтах
    uint8_t d_zero;  // Значення нуля АЦП (128)
} channel_config_t;

// Декодування сирого масиву байтів у масив напруг
void parse_waveform_bytes(const uint8_t *raw_bytes, float *voltages, size_t count, const channel_config_t *cfg) {
    for (size_t i = 0; i < count; i++) {
        voltages[i] = ((float)raw_bytes[i] - (float)cfg->d_zero) * cfg->v_scale - cfg->v_offset;
    }
}
