#include <math.h>

float wrap_pi_fmod(float angle) {
    const float two_pi = 2.0f * (float)M_PI;
    // Зсуваємо діапазон [-π, π] у [0, 2π)
    float a = fmodf(angle + (float)M_PI, two_pi);
    if (a < 0.0f) {
        a += two_pi; // корекція від'ємного залишку
    }
    return a - (float)M_PI;
}
