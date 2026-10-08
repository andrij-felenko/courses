#include <stdint.h>

typedef struct {
    uint16_t zero_offset;
    uint16_t max_resolution; // Наприклад, 16384 для 14 біт
} zero_calib_t;

void set_zero_position(zero_calib_t *calib, uint16_t current_raw_angle) {
    calib->zero_offset = current_raw_angle % calib->max_resolution;
}

uint16_t apply_zero_offset(const zero_calib_t *calib, uint16_t raw_angle) {
    int32_t diff = (int32_t)raw_angle - (int32_t)calib->zero_offset;
    if (diff < 0) {
        diff += calib->max_resolution;
    }
    return (uint16_t)diff;
}
