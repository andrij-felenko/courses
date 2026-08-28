// Драйвер зчитування диференційного АЦП з ковзним фільтром (C99)
#include <stdint.h>
#include <stdbool.h>

#define ADC_FILTER_WINDOW   16U
#define ADC_VREF_UV         3300000UL   // 3.3 В опорна напруга в мікровольтах
#define ADC_MAX_CODE_24BIT  8388607L    // Повна шкала диференційного 24-біт коду (2^23 - 1)

typedef struct {
    int32_t samples[ADC_FILTER_WINDOW];
    uint8_t index;
    uint8_t count;
    int32_t sum;
} adc_filter_t;

void adc_filter_init(adc_filter_t *f) {
    f->index = 0;
    f->count = 0;
    f->sum = 0;
    for (uint8_t i = 0; i < ADC_FILTER_WINDOW; ++i) {
        f->samples[i] = 0;
    }
}

int32_t adc_filter_update(adc_filter_t *f, int32_t raw_code) {
    if (f->count >= ADC_FILTER_WINDOW) {
        f->sum -= f->samples[f->index];
    } else {
        f->count++;
    }
    
    f->samples[f->index] = raw_code;
    f->sum += raw_code;
    f->index = (f->index + 1U) % ADC_FILTER_WINDOW;
    
    return f->sum / (int32_t)f->count;
}

// Переведення 24-бітного диференційного коду в мікровольти
int32_t adc_code_to_microvolts(int32_t code) {
    int64_t uv = ((int64_t)code * ADC_VREF_UV) / ADC_MAX_CODE_24BIT;
    return (int32_t)uv;
}
