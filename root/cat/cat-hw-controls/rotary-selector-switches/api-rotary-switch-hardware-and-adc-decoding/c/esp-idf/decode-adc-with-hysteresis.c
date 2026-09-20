#include <stdint.h>
#include <stdbool.h>

#define NUM_POSITIONS 12
#define HYSTERESIS_ADC 35
#define ADC_ERROR_LOW  30
#define ADC_ERROR_HIGH 4065

typedef struct {
    uint16_t center_val;
    uint16_t min_val;
    uint16_t max_val;
} adc_window_t;

typedef struct {
    adc_window_t windows[NUM_POSITIONS];
    uint8_t current_pos;
    bool hardware_fault;
} rotary_adc_decoder_t;

uint8_t decode_adc_with_hysteresis(rotary_adc_decoder_t *dec, uint16_t raw_adc) {
    if (raw_adc < ADC_ERROR_LOW || raw_adc > ADC_ERROR_HIGH) {
        dec->hardware_fault = true;
        return dec->current_pos;
    }
    dec->hardware_fault = false;

    uint8_t cur = dec->current_pos;
    // Перевірка утримання поточної позиції з урахуванням розширеного вікна гістерезису
    if (raw_adc >= (dec->windows[cur].min_val - HYSTERESIS_ADC) &&
        raw_adc <= (dec->windows[cur].max_val + HYSTERESIS_ADC)) {
        return cur;
    }

    // Пошук нової позиції за точними центрами вікон
    for (uint8_t i = 0; i < NUM_POSITIONS; i++) {
        if (raw_adc >= dec->windows[i].min_val && raw_adc <= dec->windows[i].max_val) {
            dec->current_pos = i;
            break;
        }
    }
    return dec->current_pos;
}
