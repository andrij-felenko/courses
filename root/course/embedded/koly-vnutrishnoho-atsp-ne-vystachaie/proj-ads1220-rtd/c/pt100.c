#include "pt100.h"

#include <math.h>
#include <stddef.h>

/* Коефіцієнти характеристики DIN/IEC 60751 */
#define PT100_R0   100.0f
#define PT100_A    3.9083e-3f
#define PT100_B   -5.7750e-7f
#define PT100_C   -4.1830e-12f

/* Межі паспортного діапазону датчика: 18.52 Ом при -200 °C,
   390.48 Ом при 850 °C. Беремо з невеликим допуском. */
#define R_MIN      18.0f
#define R_MAX      391.0f

#define NEWTON_MAX_STEPS   5
#define NEWTON_EPS_C       1.0e-4f

float pt100_resistance_at(float t)
{
    const float t2 = t * t;
    const float t3 = t2 * t;

    /* Кубічний член працює лише нижче нуля — так визначено рівняння */
    const float cubic = (t < 0.0f) ? (PT100_C * (t - 100.0f) * t3) : 0.0f;

    return PT100_R0 * (1.0f + PT100_A * t + PT100_B * t2 + cubic);
}

pt100_status_t pt100_celsius_at(float r_ohms, float *t_celsius)
{
    if (t_celsius == NULL) {
        return PT100_ERR_ARG;
    }
    if (!(r_ohms >= R_MIN) || !(r_ohms <= R_MAX)) {
        return PT100_ERR_RANGE; /* заразом відсіює NaN */
    }

    /* Вище нуля рівняння квадратне й розв'язується аналітично */
    const float z = 1.0f - (r_ohms / PT100_R0);
    const float discriminant = (PT100_A * PT100_A) - (4.0f * PT100_B * z);
    if (discriminant < 0.0f) {
        return PT100_ERR_RANGE;
    }

    float t = (-PT100_A + sqrtf(discriminant)) / (2.0f * PT100_B);

    /* Нижче нуля додається кубічний член: аналітичний корінь стає лише
       першим наближенням, яке дотягує метод Ньютона-Рафсона. */
    if (t < 0.0f) {
        for (int i = 0; i < NEWTON_MAX_STEPS; i++) {
            const float t2 = t * t;
            const float t3 = t2 * t;

            const float r_model = pt100_resistance_at(t);
            /* dR/dT = R0·(A + 2B·T - 300C·T² + 4C·T³) */
            const float slope = PT100_R0 * (PT100_A + 2.0f * PT100_B * t
                                            - 300.0f * PT100_C * t2
                                            + 4.0f * PT100_C * t3);
            if (fabsf(slope) < 1.0e-9f) {
                return PT100_ERR_RANGE;
            }

            const float step = (r_model - r_ohms) / slope;
            t -= step;
            if (fabsf(step) < NEWTON_EPS_C) {
                break; /* два-три кроки дають похибку менше за 0.001 °C */
            }
        }
    }

    if (t < -200.0f || t > 850.0f) {
        return PT100_ERR_RANGE;
    }

    *t_celsius = t;
    return PT100_OK;
}
