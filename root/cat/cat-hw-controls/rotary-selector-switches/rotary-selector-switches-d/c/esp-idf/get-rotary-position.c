#include <stdint.h>

#define NUM_POSITIONS 12
#define ADC_MAX_VAL   4095

// Обчислення номеру позиції галети (від 1 до 12) за кодом АЦП
int get_rotary_position(uint16_t raw_adc) {
    uint16_t step = ADC_MAX_VAL / (NUM_POSITIONS - 1);
    uint16_t half_step = step / 2;
    
    for (int i = 0; i < NUM_POSITIONS; i++) {
        uint16_t target = i * step;
        uint16_t min_val = (target > half_step) ? (target - half_step) : 0;
        uint16_t max_val = (target + half_step < ADC_MAX_VAL) ? (target + half_step) : ADC_MAX_VAL;
        
        if (raw_adc >= min_val && raw_adc <= max_val) {
            return i + 1;
        }
    }
    return -1; // Хибне значення при обриві або брязкоті
}
