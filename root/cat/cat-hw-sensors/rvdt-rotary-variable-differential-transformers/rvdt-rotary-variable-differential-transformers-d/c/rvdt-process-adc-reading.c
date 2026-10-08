#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define RVDT_LUT_SIZE 17

typedef struct {
    float null_offset_rad;
    float sensitivity_per_rad;
    float lut_angles_deg[RVDT_LUT_SIZE];
    float lut_corrections_deg[RVDT_LUT_SIZE];
} rvdt_calibration_t;

float rvdt_process_adc_reading(uint16_t raw_vs1, uint16_t raw_vs2, const rvdt_calibration_t *cal) {
    float v1 = (float)raw_vs1;
    float v2 = (float)raw_vs2;
    float sum = v1 + v2;

    if (sum < 1.0f) {
        return 0.0f; // Захист від ділення на нуль при обриві збудження
    }

    float ratio = (v1 - v2) / sum;
    float raw_angle_rad = ratio / cal->sensitivity_per_rad;
    float calibrated_angle_rad = raw_angle_rad - cal->null_offset_rad;
    float angle_deg = calibrated_angle_rad * (180.0f / 3.14159265f);

    // Таблична інтерполяція синусоїдальної нелінійності
    if (angle_deg <= cal->lut_angles_deg[0]) {
        return angle_deg + cal->lut_corrections_deg[0];
    }
    if (angle_deg >= cal->lut_angles_deg[RVDT_LUT_SIZE - 1]) {
        return angle_deg + cal->lut_corrections_deg[RVDT_LUT_SIZE - 1];
    }

    for (int i = 0; i < RVDT_LUT_SIZE - 1; i++) {
        if (angle_deg >= cal->lut_angles_deg[i] && angle_deg <= cal->lut_angles_deg[i + 1]) {
            float t = (angle_deg - cal->lut_angles_deg[i]) / (cal->lut_angles_deg[i + 1] - cal->lut_angles_deg[i]);
            float corr = cal->lut_corrections_deg[i] + t * (cal->lut_corrections_deg[i + 1] - cal->lut_corrections_deg[i]);
            return angle_deg + corr;
        }
    }

    return angle_deg;
}
