#include <math.h>

float calculate_dew_point(float temp, float humidity) {
    const float b = 17.67f;
    const float c = 243.5f;
    float gamma = logf(humidity / 100.0f) + (b * temp) / (c + temp);
    return (c * gamma) / (b - gamma);
}

float calculate_absolute_humidity(float temp, float humidity) {
    const float a = 6.112f;
    const float b = 17.67f;
    const float c = 243.5f;
    float p_s = a * expf((b * temp) / (c + temp));
    float p_a = p_s * (humidity / 100.0f);
    return (216.7f * p_a) / (273.15f + temp);
}
