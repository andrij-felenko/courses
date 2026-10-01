#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "beam_profiler.h"

#define WIDTH 64
#define HEIGHT 64

// Генерація тестового кадру з Гауссовим лазерним пучком та шумом
static void generate_synthetic_frame(
    uint16_t *frame,
    uint16_t *dark,
    size_t w,
    size_t h,
    double true_cx,
    double true_cy,
    double true_wx,
    double true_wy
) {
    for (size_t y = 0; y < h; ++y) {
        for (size_t x = 0; x < w; ++x) {
            size_t idx = y * w + x;
            
            // Темновий кадр (темновий струм сенсора + шум)
            uint16_t bg = 100 + (uint16_t)(rand() % 15);
            dark[idx] = bg;

            // Гауссів профіль інтенсивності I(x,y) = I0 * exp(-2*((x-cx)^2/wx^2 + (y-cy)^2/wy^2))
            double dx = (double)x - true_cx;
            double dy = (double)y - true_cy;
            double val = 3000.0 * exp(-2.0 * (dx * dx / (true_wx * true_wx) + dy * dy / (true_wy * true_wy)));
            
            frame[idx] = bg + (uint16_t)val + (uint16_t)(rand() % 10);
        }
    }
}

int main(void) {
    printf("=== Демонстрація аналізу профілю лазерного пучка (ISO 11146) ===\n");

    size_t width = WIDTH;
    size_t height = HEIGHT;
    size_t pixel_count = width * height;

    uint16_t *raw_frame = (uint16_t *)malloc(pixel_count * sizeof(uint16_t));
    uint16_t *dark_frame = (uint16_t *)malloc(pixel_count * sizeof(uint16_t));
    float *corrected_frame = (float *)malloc(pixel_count * sizeof(float));

    if (!raw_frame || !dark_frame || !corrected_frame) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(raw_frame);
        free(dark_frame);
        free(corrected_frame);
        return EXIT_FAILURE;
    }

    // Задаємо істинні параметри синтетичного Гауссового пучка (ширина 1/e^2 = 12 пікселів)
    double true_cx = 31.5;
    double true_cy = 31.5;
    double true_w = 12.0;
    generate_synthetic_frame(raw_frame, dark_frame, width, height, true_cx, true_cy, true_w, true_w);

    // 1. Фонове віднімання та фільтрація шуму
    float noise_threshold = 20.0f;
    if (!beam_profiler_subtract_dark(raw_frame, dark_frame, corrected_frame, width, height, noise_threshold)) {
        fprintf(stderr, "Помилка при обробці фону кадру\n");
        free(raw_frame);
        free(dark_frame);
        free(corrected_frame);
        return EXIT_FAILURE;
    }

    // 2. Обчислення просторових моментів ISO 11146
    beam_params_t params;
    if (!beam_profiler_compute(corrected_frame, width, height, &params)) {
        fprintf(stderr, "Помилка обчислення моментів пучка\n");
        free(raw_frame);
        free(dark_frame);
        free(corrected_frame);
        return EXIT_FAILURE;
    }

    // 3. Виведення результатів
    printf("Центроїд пучка (X, Y):       (%.2f, %.2f) пікс.\n", params.cx, params.cy);
    printf("Сумарна інтенсивність P:    %.1f ADU\n", params.total_power);
    printf("Моменти (sig_x2, sig_y2):   (%.2f, %.2f)\n", params.sigma_x2, params.sigma_y2);
    printf("Діаметр D4sigma (major):    %.2f пікс.\n", params.d4s_major);
    printf("Діаметр D4sigma (minor):    %.2f пікс.\n", params.d4s_minor);
    printf("Еліптичність:               %.3f\n", params.ellipticity);
    printf("Кут орієнтації:             %.2f град.\n", params.orientation_rad * 180.0 / M_PI);

    free(raw_frame);
    free(dark_frame);
    free(corrected_frame);
    return EXIT_SUCCESS;
}
