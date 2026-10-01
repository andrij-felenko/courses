#include "beam_profiler.h"
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

bool beam_profiler_subtract_dark(
    const uint16_t *frame,
    const uint16_t *dark,
    float *corrected,
    size_t width,
    size_t height,
    float noise_threshold
) {
    if (!frame || !corrected || width == 0 || height == 0) {
        return false;
    }

    size_t total_pixels = width * height;
    for (size_t i = 0; i < total_pixels; ++i) {
        float dark_val = dark ? (float)dark[i] : 0.0f;
        float val = (float)frame[i] - dark_val;

        // Порогова фільтрація фонового шуму
        if (val < noise_threshold) {
            corrected[i] = 0.0f;
        } else {
            corrected[i] = val - noise_threshold;
        }
    }

    return true;
}

bool beam_profiler_compute(
    const float *corrected,
    size_t width,
    size_t height,
    beam_params_t *params
) {
    if (!corrected || !params || width == 0 || height == 0) {
        return false;
    }

    double P = 0.0;
    double sum_x = 0.0;
    double sum_y = 0.0;

    // Перший прохід: обчислення сумарної потужності P та взважених координат (центроїда)
    for (size_t y = 0; y < height; ++y) {
        size_t row_offset = y * width;
        for (size_t x = 0; x < width; ++x) {
            double val = (double)corrected[row_offset + x];
            if (val > 0.0) {
                P += val;
                sum_x += (double)x * val;
                sum_y += (double)y * val;
            }
        }
    }

    if (P <= 0.0) {
        return false; // Пучок відсутній або значення нижче порогу
    }

    double cx = sum_x / P;
    double cy = sum_y / P;

    // Другий прохід: обчислення других центральних моментів (sigma_x2, sigma_y2, sigma_xy)
    double s_x2 = 0.0;
    double s_y2 = 0.0;
    double s_xy = 0.0;

    for (size_t y = 0; y < height; ++y) {
        size_t row_offset = y * width;
        double dy = (double)y - cy;
        for (size_t x = 0; x < width; ++x) {
            double val = (double)corrected[row_offset + x];
            if (val > 0.0) {
                double dx = (double)x - cx;
                s_x2 += dx * dx * val;
                s_y2 += dy * dy * val;
                s_xy += dx * dy * val;
            }
        }
    }

    s_x2 /= P;
    s_y2 /= P;
    s_xy /= P;

    // Розрахунок параметрів еліптичності та діаметрів D4sigma за стандартом ISO 11146
    double diff = s_x2 - s_y2;
    double discriminant = sqrt(diff * diff + 4.0 * s_xy * s_xy);

    double d4s_major = 2.0 * sqrt(2.0 * (s_x2 + s_y2 + discriminant));
    double d4s_minor = 2.0 * sqrt(2.0 * (s_x2 + s_y2 - discriminant));

    // Азимутальний кут орієнтації головної осі
    double theta = 0.5 * atan2(2.0 * s_xy, diff);

    params->total_power = P;
    params->cx = cx;
    params->cy = cy;
    params->sigma_x2 = s_x2;
    params->sigma_y2 = s_y2;
    params->sigma_xy = s_xy;
    params->d4s_major = d4s_major;
    params->d4s_minor = d4s_minor;
    params->orientation_rad = theta;
    params->ellipticity = (d4s_major > 0.0) ? (d4s_minor / d4s_major) : 1.0;

    return true;
}
