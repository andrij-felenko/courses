#include <math.h>
#include <stdbool.h>

// Коефіцієнти стандарту IEC 60751 для PT100
#define RTD_R0 100.0f
#define RTD_A  3.9083e-3f
#define RTD_B  -5.775e-7f
#define RTD_C  -4.183e-12f

float rtd_calc_temperature_negative(float r_meas) {
    // Початкове наближення за точним аналітичним квадратичним розв'язком
    float poly_discr = RTD_A * RTD_A - 4.0f * RTD_B * (1.0f - r_meas / RTD_R0);
    float t = (-RTD_A + sqrtf(poly_discr)) / (2.0f * RTD_B);

    if (t >= 0.0f) {
        return t; // Для t >= 0 додаткова чисельна корекція не потрібна
    }

    // Ітерації Ньютона — Рафсона для від'ємних температур (максимум 3 ітерації)
    for (int i = 0; i < 3; i++) {
        float t2 = t * t;
        float t3 = t2 * t;
        float t4 = t3 * t;

        // Значення f(t) = R(t) - R_meas
        float f_val = RTD_R0 * (1.0f + RTD_A * t + RTD_B * t2 + RTD_C * (t - 100.0f) * t3) - r_meas;

        // Похідна f'(t) = dR/dt
        float f_deriv = RTD_R0 * (RTD_A + 2.0f * RTD_B * t + 4.0f * RTD_C * t3 - 300.0f * RTD_C * t2);

        float delta = f_val / f_deriv;
        t -= delta;

        if (fabsf(delta) < 1e-4f) {
            break; // Збіжність досягнута з високою точністю
        }
    }

    return t;
}
