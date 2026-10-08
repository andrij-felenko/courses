#include <math.h>

/* Структура калібрувальних коефіцієнтів аналогового тракту */
typedef struct {
    float off_cos;     /* Постійний зсув косинуса, В */
    float off_sin;     /* Постійний зсув синуса, В */
    float gain_ratio;  /* Співвідношення амплітуд (A_cos / A_sin) */
    float sin_phi;     /* Синус кута фазового відхилення sin(phi_err) */
    float cos_phi;     /* Косинус кута фазового відхилення cos(phi_err) */
} sensor_calib_t;

/* Обчислення абсолютного кута в градусах [0..360) з повною матричною корекцією */
float calculate_calibrated_angle(float raw_cos, float raw_sin, const sensor_calib_t *cal) {
    /* 1. Усунення постійного зсуву нуля (офсету) */
    float v_c_norm = raw_cos - cal->off_cos;
    float v_s_norm = (raw_sin - cal->off_sin) * cal->gain_ratio;
    
    /* 2. Ортогоналізація фазового зсуву (компенсація похибки 90 градусів) */
    float v_cos_corr = v_c_norm;
    float v_sin_corr = (v_s_norm - v_c_norm * cal->sin_phi) / cal->cos_phi;
    
    /* 3. Обчислення арктангенса двох аргументів */
    float angle_rad = atan2f(v_sin_corr, v_cos_corr);
    float angle_deg = angle_rad * (180.0f / 3.14159265358979323846f);
    
    /* 4. Нормалізація результату до діапазону [0, 360) градусів */
    if (angle_deg < 0.0f) {
        angle_deg += 360.0f;
    }
    return angle_deg;
}
