#include <stdint.h>

// Таблиця переходів квадратурного автомата станів (1X / 4X)
static const int8_t encoder_table[16] = {
    0,  1, -1,  0,
   -1,  0,  0,  1,
    1,  0,  0, -1,
    0, -1,  1,  0
};

static volatile int32_t encoder_counter = 0;
static uint8_t prev_state = 0;

void IRAM_ATTR encoder_isr_handler(uint8_t curr_a, uint8_t curr_b) {
    uint8_t curr_state = (curr_a << 1) | curr_b;
    uint8_t index = (prev_state << 2) | curr_state;
    encoder_counter += encoder_table[index];
    prev_state = curr_state;
}
