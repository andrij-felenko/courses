#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

typedef struct {
    float offset_sin_v;
    float offset_cos_v;
    float scale_sin;
    float scale_cos;
    float vref_v;
} scott_t_calib_t;

typedef struct {
    float angle_rad;
    float angle_deg;
    bool is_valid;
} scott_t_result_t;

/* Розрахунок кута за оцифрованими значеннями АЦП з калібруванням зсуву та масштабу */
scott_t_result_t scott_t_compute_angle(uint16_t adc_sin, uint16_t adc_cos, uint16_t adc_max, const scott_t_calib_t *calib) {
    scott_t_result_t res = {0.0f, 0.0f, false};
    if (!calib || adc_max == 0) return res;

    // Переведення кодів АЦП у напруги
    float v_sin = ((float)adc_sin / (float)adc_max) * calib->vref_v;
    float v_cos = ((float)adc_cos / (float)adc_max) * calib->vref_v;

    // Віднімання постійного зсуву (VREF / 2) та калібрувального офсету
    float norm_sin = (v_sin - calib->offset_sin_v) * calib->scale_sin;
    float norm_cos = (v_cos - calib->offset_cos_v) * calib->scale_cos;

    // Перевірка мінімальної амплітуди сигналу (виявлення обриву)
    float magnitude_sq = norm_sin * norm_sin + norm_cos * norm_cos;
    if (magnitude_sq < 0.01f) {
        res.is_valid = false;
        return res;
    }

    // Обчислення абсолютного кута ротора через atan2f
    float angle = atan2f(norm_sin, norm_cos);
    if (angle < 0.0f) {
        angle += 2.0f * (float)M_PI;
    }

    res.angle_rad = angle;
    res.angle_deg = angle * (180.0f / (float)M_PI);
    res.is_valid = true;
    return res;
}
