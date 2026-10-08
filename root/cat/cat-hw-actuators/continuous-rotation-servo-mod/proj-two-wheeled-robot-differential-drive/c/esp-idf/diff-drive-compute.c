#include <math.h>

typedef struct {
    float track_width; // Колійна база B (м)
    float k_trim_left; // Коефіціент вирівнювання лівого борта
    float k_trim_right;// Коефіцієнт вирівнювання правого борта
} diff_drive_config_t;

void diff_drive_compute(float v, float omega, const diff_drive_config_t *cfg, 
                       float *speed_left, float *speed_right) {
    // Обернена кінематика
    float v_l = v - (omega * cfg->track_width / 2.0f);
    float v_r = v + (omega * cfg->track_width / 2.0f);

    // Застосовуємо трим-коефіцієнти для компенсації асиметрії
    *speed_left  = v_l * cfg->k_trim_left;
    *speed_right = v_r * cfg->k_trim_right;
}
