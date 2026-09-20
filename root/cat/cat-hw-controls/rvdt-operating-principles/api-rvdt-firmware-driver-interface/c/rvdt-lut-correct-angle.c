#include <stddef.h>

#define LUT_SIZE 5

typedef struct {
    float x_nodes[LUT_SIZE]; // Виміряні сирі кути (рад)
    float y_nodes[LUT_SIZE]; // Еталонні точні кути (рад)
} rvdt_lut_t;

float rvdt_lut_correct_angle(const rvdt_lut_t *lut, float raw_angle) {
    if (raw_angle <= lut->x_nodes[0]) {
        return lut->y_nodes[0];
    }
    if (raw_angle >= lut->x_nodes[LUT_SIZE - 1]) {
        return lut->y_nodes[LUT_SIZE - 1];
    }

    for (size_t i = 0; i < LUT_SIZE - 1; ++i) {
        if (raw_angle >= lut->x_nodes[i] && raw_angle <= lut->x_nodes[i + 1]) {
            float dx = raw_angle - lut->x_nodes[i];
            float dx_span = lut->x_nodes[i + 1] - lut->x_nodes[i];
            float dy_span = lut->y_nodes[i + 1] - lut->y_nodes[i];
            float slope = dy_span / dx_span;
            return lut->y_nodes[i] + dx * slope;
        }
    }
    return raw_angle;
}
