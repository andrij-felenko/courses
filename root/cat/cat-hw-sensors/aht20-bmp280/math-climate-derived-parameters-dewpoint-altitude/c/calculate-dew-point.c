#include <math.h>
#include <stdbool.h>

#define MAGNUS_A 17.27f
#define MAGNUS_B 237.7f

// Обчислення точки роси за формулою Магнуса — Тетенса
bool calculate_dew_point(float temp_c, float rh_pct, float *dew_point) {
    if (rh_pct <= 0.0f || rh_pct > 100.0f || temp_c < -40.0f || temp_c > 85.0f) {
        return false; // Похибка діапазону вхідних даних
    }
    float gamma = (MAGNUS_A * temp_c) / (MAGNUS_B + temp_c) + logf(rh_pct / 100.0f);
    *dew_point = (MAGNUS_B * gamma) / (MAGNUS_A - gamma);
    return true;
}

// Обчислення барометричної висоти щодо опорного тиску QNH
float calculate_altitude(float pressure_hpa, float qnh_hpa) {
    if (qnh_hpa <= 0.0f || pressure_hpa <= 0.0f) {
        return 0.0f;
    }
    float ratio = pressure_hpa / qnh_hpa;
    return 44330.77f * (1.0f - powf(ratio, 0.190263f));
}
