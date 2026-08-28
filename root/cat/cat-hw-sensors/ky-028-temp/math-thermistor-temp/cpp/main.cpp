#include <math.h>

// паспортні сталі термістора
const float R0 = 10000.0f;    // опір за опорної температури, Ом
const float T0 = 298.15f;     // опорна температура, КЕЛЬВІНИ (25 °C)
const float B  = 3950.0f;     // стала Бета, K

// температура (°C) з виміряного опору термістора (Ом)
float tempFromResistance(float R) {
    float invT = 1.0f / T0 + (1.0f / B) * logf(R / R0);  // 1/T у 1/K
    float tK   = 1.0f / invT;                             // назад у кельвіни
    return tK - 273.15f;                                  // у °C
}
