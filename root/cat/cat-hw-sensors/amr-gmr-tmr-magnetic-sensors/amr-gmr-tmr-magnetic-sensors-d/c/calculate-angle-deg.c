#include <math.h>

/* Обчислення абсолютного кута в градусах [0..360) з компенсацією офсету та дисбалансу */
float calculate_angle_deg(float v_sin, float v_cos, float off_sin, float off_cos, float gain_ratio) {
    float sin_corr = v_sin - off_sin;
    float cos_corr = (v_cos - off_cos) * gain_ratio;
    
    float angle_rad = atan2f(sin_corr, cos_corr);
    float angle_deg = angle_rad * (180.0f / 3.14159265358979323846f);
    
    if (angle_deg < 0.0f) {
        angle_deg += 360.0f;
    }
    return angle_deg;
}
