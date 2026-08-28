#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура для збереження фізичних параметрів установки
typedef struct {
    double wavelength; // Довжина хвилі λ (м)
    double d;          // Відстань між центрами щілин d (м)
    double a;          // Ширина однієї щілини a (м)
    double L;          // Відстань від ширми до екрана L (м)
    double gamma;      // Ступінь просторової когерентності [0.0..1.0]
} DoubleSlitParams;

// Чисельне обчислення нормованої інтенсивності у точці y
double compute_intensity(const DoubleSlitParams* p, double y) {
    if (p->L <= 0.0 || p->wavelength <= 0.0) return 0.0;

    double sin_theta = y / sqrt(y * y + p->L * p->L);
    double alpha = (M_PI * p->d * sin_theta) / p->wavelength;
    double beta  = (M_PI * p->a * sin_theta) / p->wavelength;

    double interference = 1.0 + p->gamma * cos(2.0 * alpha);

    double diffraction = 1.0;
    if (fabs(beta) > 1e-7) {
        double sinc = sin(beta) / beta;
        diffraction = sinc * sinc;
    } else {
        diffraction = 1.0 - (beta * beta) / 3.0; // Тейлор для стійкості
    }

    return interference * diffraction;
}

// Вивід текстової ASCII-картини інтерференційного профілю
void print_ascii_pattern(const DoubleSlitParams* p, double y_max, int steps, int bar_width) {
    printf("=== Двощілинна інтерференція (C) ===\n");
    printf("Параметри: λ = %.1f нм, d = %.2f мм, a = %.2f мм, L = %.1f м, γ = %.2f\n\n",
           p->wavelength * 1e9, p->d * 1e3, p->a * 1e3, p->L, p->gamma);

    double dy = (2.0 * y_max) / (steps - 1);
    for (int i = 0; i < steps; ++i) {
        double y = -y_max + i * dy;
        double intensity = compute_intensity(p, y);

        int stars = (int)(intensity * bar_width / 2.0);
        printf("%+6.2f мм | ", y * 1e3);
        for (int s = 0; s < stars; ++s) {
            putchar('*');
        }
        printf(" (%.3f)\n", intensity);
    }
}

int main(void) {
    DoubleSlitParams params = {
        .wavelength = 632.8e-9, // Червоний He-Ne лазер
        .d = 0.2e-3,            // 0.2 мм між щілинами
        .a = 0.04e-3,           // 0.04 мм ширина щілини
        .L = 2.0,               // 2.0 м до екрана
        .gamma = 1.0            // Повна когерентність
    };

    print_ascii_pattern(&params, 0.015, 21, 40);
    return 0;
}
