#include <stdint.h>
#include <math.h>

// Обчислення ZNCC для одного фрагмента зображення
float compute_zncc_window(const uint8_t *img, int img_stride,
                          const uint8_t *tpl, int tpl_stride,
                          int w, int h) {
    double sum_i = 0.0, sum_t = 0.0;
    const double area = (double)(w * h);

    for (int y = 0; y < h; ++y) {
        const uint8_t *i_ptr = img + y * img_stride;
        const uint8_t *t_ptr = tpl + y * tpl_stride;
        for (int x = 0; x < w; ++x) {
            sum_i += (double)i_ptr[x];
            sum_t += (double)t_ptr[x];
        }
    }

    const double mean_i = sum_i / area;
    const double mean_t = sum_t / area;

    double num = 0.0;
    double var_i = 0.0;
    double var_t = 0.0;

    for (int y = 0; y < h; ++y) {
        const uint8_t *i_ptr = img + y * img_stride;
        const uint8_t *t_ptr = tpl + y * tpl_stride;
        for (int x = 0; x < w; ++x) {
            const double di = (double)i_ptr[x] - mean_i;
            const double dt = (double)t_ptr[x] - mean_t;
            num += di * dt;
            var_i += di * di;
            var_t += dt * dt;
        }
    }

    const double denom = sqrt(var_i * var_t);
    if (denom < 1e-7) return 0.0f; // Однорідне поле
    return (float)(num / denom);
}
