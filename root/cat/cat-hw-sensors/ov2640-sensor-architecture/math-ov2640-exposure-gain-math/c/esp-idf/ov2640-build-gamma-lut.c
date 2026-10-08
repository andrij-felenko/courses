#include <stdint.h>
#include <math.h>

#define OV2640_GAMMA_NODES 15

typedef struct {
    uint8_t x_nodes[OV2640_GAMMA_NODES];
    uint8_t y_nodes[OV2640_GAMMA_NODES];
    uint16_t slopes[OV2640_GAMMA_NODES - 1]; // Фіксована кома Q8.8
} ov2640_gamma_lut_t;

void ov2640_build_gamma_lut(float gamma, ov2640_gamma_lut_t *lut) {
    if (!lut || gamma <= 0.0f) return;
    float inv_gamma = 1.0f / gamma;

    // Вузлові точки X із більшою щільністю у тінях
    static const uint8_t x_defaults[OV2640_GAMMA_NODES] = {
        0, 4, 8, 16, 24, 32, 48, 64, 80, 96, 128, 160, 192, 224, 255
    };

    for (int i = 0; i < OV2640_GAMMA_NODES; i++) {
        lut->x_nodes[i] = x_defaults[i];
        float norm_x = (float)x_defaults[i] / 255.0f;
        float norm_y = powf(norm_x, inv_gamma);
        lut->y_nodes[i] = (uint8_t)roundf(norm_y * 255.0f);
    }

    for (int i = 0; i < OV2640_GAMMA_NODES - 1; i++) {
        uint8_t dx = lut->x_nodes[i + 1] - lut->x_nodes[i];
        int16_t dy = (int16_t)lut->y_nodes[i + 1] - (int16_t)lut->y_nodes[i];
        lut->slopes[i] = (uint16_t)((dy * 256) / dx);
    }
}

uint8_t ov2640_apply_gamma(uint8_t x_in, const ov2640_gamma_lut_t *lut) {
    if (x_in <= lut->x_nodes[0]) return lut->y_nodes[0];
    if (x_in >= lut->x_nodes[OV2640_GAMMA_NODES - 1]) return lut->y_nodes[OV2640_GAMMA_NODES - 1];

    int segment = 0;
    while (segment < OV2640_GAMMA_NODES - 2 && x_in >= lut->x_nodes[segment + 1]) {
        segment++;
    }

    uint8_t dx = x_in - lut->x_nodes[segment];
    uint16_t dy_scaled = (dx * lut->slopes[segment]) >> 8;
    return lut->y_nodes[segment] + (uint8_t)dy_scaled;
}
