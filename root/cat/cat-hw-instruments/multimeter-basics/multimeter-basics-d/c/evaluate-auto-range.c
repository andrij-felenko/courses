#include <stdint.h>
#include <stdbool.h>

typedef enum {
    RANGE_200mV = 0,
    RANGE_2V,
    RANGE_20V,
    RANGE_200V,
    RANGE_1000V,
    RANGE_COUNT
} voltage_range_t;

typedef struct {
    voltage_range_t current_range;
    uint16_t max_adc_counts;
    uint16_t min_adc_counts;
} multimeter_state_t;

voltage_range_t evaluate_auto_range(multimeter_state_t *state, uint16_t raw_counts) {
    // Перевірка перевищення верхньої межі шкали (переповнення)
    if (raw_counts >= state->max_adc_counts && state->current_range < RANGE_1000V) {
        return (voltage_range_t)(state->current_range + 1);
    }
    // Перевірка падіння залишку нижче 10% від шкали
    if (raw_counts < state->min_adc_counts && state->current_range > RANGE_200mV) {
        return (voltage_range_t)(state->current_range - 1);
    }
    return state->current_range;
}
