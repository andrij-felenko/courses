#ifndef BEAM_PROFILER_H
#define BEAM_PROFILER_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

// Результати обчислення параметрів лазерного пучка за ISO 11146
typedef struct {
    double total_power;    // Сумарна інтенсивність P
    double cx;             // Центр мас пучка по осі X (пікселі)
    double cy;             // Центр мас пучка по осі Y (пікселі)
    double sigma_x2;       // Другий центральний момент sigma_x^2
    double sigma_y2;       // Другий центральний момент sigma_y^2
    double sigma_xy;       // Перехресний другий момент sigma_xy
    double d4s_major;      // Основний діаметр пучка D4sigma (пікселі)
    double d4s_minor;      // Другорядний діаметр пучка D4sigma (пікселі)
    double orientation_rad;// Кут орієнтації головної осі еліпса (радіани)
    double ellipticity;    // Еліптичність (d4s_minor / d4s_major)
} beam_params_t;

// Фонове віднімання темнового кадру та порогове відсікання шумів
bool beam_profiler_subtract_dark(
    const uint16_t *frame,
    const uint16_t *dark,
    float *corrected,
    size_t width,
    size_t height,
    float noise_threshold
);

// Обчислення просторових моментів та параметрів пучка ISO 11146
bool beam_profiler_compute(
    const float *corrected,
    size_t width,
    size_t height,
    beam_params_t *params
);

#endif // BEAM_PROFILER_H
