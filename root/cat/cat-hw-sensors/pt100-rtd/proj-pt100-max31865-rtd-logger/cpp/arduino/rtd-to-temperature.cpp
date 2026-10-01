#include <Arduino.h>
#include <math.h>

// Константи рівняння Каллендара — Ван Дюзена для PT100
static const float RTD_R0 = 100.0f;
static const float CVD_A  = 3.9083e-3f;
static const float CVD_B  = -5.775e-7f;

float rtd_to_temperature(float r_rtd) {
    if (r_rtd <= 0.0f) {
        return NAN;
    }
    // Перевірка додатного діапазону (R >= 100 Ом відповідає t >= 0 °C)
    if (r_rtd >= RTD_R0) {
        float discriminant = CVD_A * CVD_A - 4.0f * CVD_B * (1.0f - r_rtd / RTD_R0);
        if (discriminant < 0.0f) {
            return NAN;
        }
        return (-CVD_A + sqrtf(discriminant)) / (2.0f * CVD_B);
    } else {
        // Поліноміальна апроксимація для t < 0 °C
        float r_poly = r_rtd;
        float t = -242.02f + 2.2228f * r_poly + 2.5859e-3f * powf(r_poly, 2) 
                  - 4.8260e-6f * powf(r_poly, 3) - 2.8183e-8f * powf(r_poly, 4) 
                  + 1.5243e-10f * powf(r_poly, 5);
        return t;
    }
}
