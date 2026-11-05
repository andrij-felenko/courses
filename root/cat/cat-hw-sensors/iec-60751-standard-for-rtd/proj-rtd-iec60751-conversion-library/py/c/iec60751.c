#include "iec60751.h"
#include <math.h>
#include <stdlib.h>

static const double A = 3.9083e-3;
static const double B = -5.7750e-7;
static const double C = -4.1830e-12;

void iec60751_init(IEC60751* sensor, double r0) {
    sensor->r0 = r0;
}

double iec60751_temp_to_res(const IEC60751* sensor, double t) {
    if (t >= 0.0) {
        return sensor->r0 * (1.0 + A * t + B * t * t);
    } else {
        return sensor->r0 * (1.0 + A * t + B * t * t + C * (t - 100.0) * t * t * t);
    }
}

double iec60751_res_to_temp(const IEC60751* sensor, double r) {
    if (r >= sensor->r0) {
        return (-A + sqrt(A * A - 4.0 * B * (1.0 - r / sensor->r0))) / (2.0 * B);
    } else {
        double t_guess = (r / sensor->r0 - 1.0) / A;
        for (int i = 0; i < 5; ++i) {
            double f = sensor->r0 * (1.0 + A * t_guess + B * t_guess * t_guess + C * (t_guess - 100.0) * t_guess * t_guess * t_guess) - r;
            double df = sensor->r0 * (A + 2.0 * B * t_guess + 4.0 * C * t_guess * t_guess * t_guess - 300.0 * C * t_guess * t_guess);
            t_guess -= f / df;
        }
        return t_guess;
    }
}

void lut_init(LookupTable* lut, const IEC60751* sensor, double t_min, double t_max, double step) {
    lut->t_min = t_min;
    lut->step = step;
    lut->size = (size_t)((t_max - t_min) / step) + 1;
    lut->resistances = (double*)malloc(lut->size * sizeof(double));
    lut->temperatures = (double*)malloc(lut->size * sizeof(double));

    for (size_t i = 0; i < lut->size; ++i) {
        double t = t_min + i * step;
        lut->temperatures[i] = t;
        lut->resistances[i] = iec60751_temp_to_res(sensor, t);
    }
}

void lut_free(LookupTable* lut) {
    free(lut->resistances);
    free(lut->temperatures);
    lut->size = 0;
}

double lut_lookup_temp(const LookupTable* lut, double r) {
    if (lut->size == 0) return 0.0;
    if (r <= lut->resistances[0]) return lut->temperatures[0];
    if (r >= lut->resistances[lut->size - 1]) return lut->temperatures[lut->size - 1];

    size_t low = 0;
    size_t high = lut->size - 1;
    while (high - low > 1) {
        size_t mid = low + (high - low) / 2;
        if (lut->resistances[mid] <= r) {
            low = mid;
        } else {
            high = mid;
        }
    }

    double r0 = lut->resistances[low];
    double r1 = lut->resistances[high];
    double t0 = lut->temperatures[low];
    double t1 = lut->temperatures[high];

    return t0 + (r - r0) * (t1 - t0) / (r1 - r0);
}
