#include <math.h>

// точка роси (°C) з температури й відносної вологості — формула Магнуса
float dew_point(float t_c, float rh_pct) {
    const float a = 17.62f, b = 243.12f;        // сталі Магнуса (над водою)
    float gamma = logf(rh_pct / 100.0f) + a * t_c / (b + t_c);
    return b * gamma / (a - gamma);             // °C
}

// тепле сухе повітря: давач показує 30 °C, 26 % RH
float td = dew_point(30.0f, 26.0f);             // ≈ 8.4 °C
