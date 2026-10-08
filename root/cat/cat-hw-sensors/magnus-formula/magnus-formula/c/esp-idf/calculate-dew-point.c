#include <math.h>

// Обчислення точки роси за формулою Магнуса-Тетенса
float calculate_dew_point(float temp_c, float rh_percent) {
    const float b = 17.67f;
    const float c = 243.5f;

    if (rh_percent <= 0.0f) {
        return -999.0f; // Захист від некоректного значення вологості
    }

    float gamma = (b * temp_c) / (c + temp_c) + logf(rh_percent / 100.0f);
    float dew_point = (c * gamma) / (b - gamma);

    return dew_point;
}
