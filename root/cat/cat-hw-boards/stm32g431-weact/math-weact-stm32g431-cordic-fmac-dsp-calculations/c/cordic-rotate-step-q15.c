// C-реалізація ітераційного кроку CORDIC у форматі з фіксованою комою Q1.15
#include <stdint.h>

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} cordic_q15_state_t;

// Таблиця кутів gamma_i = arctan(2^-i) у форматі BAM Q15 (180 deg = 32768)
static const int16_t cordic_lut_q15[15] = {
    8192, 4836, 2555, 1297, 651, 326, 163, 81, 41, 20, 10, 5, 3, 1, 1
};

void cordic_rotate_step_q15(cordic_q15_state_t *state, uint8_t i) {
    int16_t d = (state->z >= 0) ? 1 : -1;
    int16_t x_shift = state->x >> i;
    int16_t y_shift = state->y >> i;
    
    if (d > 0) {
        state->x -= y_shift;
        state->y += x_shift;
        state->z -= cordic_lut_q15[i];
    } else {
        state->x += y_shift;
        state->y -= x_shift;
        state->z += cordic_lut_q15[i];
    }
}
