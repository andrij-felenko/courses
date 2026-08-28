/* C Implementation — 1D Fresnel & Fraunhofer Wave Diffraction Engine */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для подання комплексного числа з подвійною точністю */
typedef struct {
    double real;
    double imag;
} ComplexDouble;

static inline ComplexDouble complex_add(ComplexDouble a, ComplexDouble b) {
    ComplexDouble r = { a.real + b.real, a.imag + b.imag };
    return r;
}

static inline ComplexDouble complex_mul_scalar(ComplexDouble a, double s) {
    ComplexDouble r = { a.real * s, a.imag * s };
    return r;
}

static inline ComplexDouble complex_exp_i(double phase) {
    ComplexDouble r = { cos(phase), sin(phase) };
    return r;
}

static inline double complex_abs_sq(ComplexDouble a) {
    return a.real * a.real + a.imag * a.imag;
}

/* Обчислення дифракції Фраунгофера у далекому полі */
int calc_fraunhofer_1d(
    double wavelength,
    double slit_width,
    int n_aperture,
    double screen_width,
    int n_screen,
    double distance_z,
    double* out_intensity
) {
    if (!out_intensity || n_aperture <= 0 || n_screen <= 0 || distance_z <= 0.0) {
        return -1;
    }

    double k = 2.0 * M_PI / wavelength;
    double dx_in = (slit_width * 3.0) / n_aperture;
    double dx_out = screen_width / n_screen;

    for (int k_idx = 0; k_idx < n_screen; ++k_idx) {
        double x_out = -screen_width / 2.0 + k_idx * dx_out;
        double sin_theta = x_out / sqrt(x_out * x_out + distance_z * distance_z);

        ComplexDouble sum = { 0.0, 0.0 };

        for (int j = 0; j < n_aperture; ++j) {
            double x_in = - (slit_width * 1.5) + j * dx_in;
            
            /* Перевірка перебування всередині щілини [-a/2, +a/2] */
            if (fabs(x_in) <= slit_width / 2.0) {
                double phase = -k * sin_theta * x_in;
                ComplexDouble c = complex_exp_i(phase);
                sum = complex_add(sum, c);
            }
        }

        sum = complex_mul_scalar(sum, dx_in);
        out_intensity[k_idx] = complex_abs_sq(sum) / (wavelength * distance_z);
    }

    return 0;
}

/* Обчислення дифракції Френеля у близькому полі */
int calc_fresnel_1d(
    double wavelength,
    double slit_width,
    int n_aperture,
    double screen_width,
    int n_screen,
    double distance_z,
    double* out_intensity
) {
    if (!out_intensity || n_aperture <= 0 || n_screen <= 0 || distance_z <= 0.0) {
        return -1;
    }

    double coeff_phase = M_PI / (wavelength * distance_z);
    double dx_in = (slit_width * 3.0) / n_aperture;
    double dx_out = screen_width / n_screen;

    for (int k_idx = 0; k_idx < n_screen; ++k_idx) {
        double x_out = -screen_width / 2.0 + k_idx * dx_out;
        ComplexDouble sum = { 0.0, 0.0 };

        for (int j = 0; j < n_aperture; ++j) {
            double x_in = - (slit_width * 1.5) + j * dx_in;

            if (fabs(x_in) <= slit_width / 2.0) {
                double diff_x = x_out - x_in;
                double phase = coeff_phase * (diff_x * diff_x);
                ComplexDouble c = complex_exp_i(phase);
                sum = complex_add(sum, c);
            }
        }

        sum = complex_mul_scalar(sum, dx_in);
        out_intensity[k_idx] = complex_abs_sq(sum) / (wavelength * distance_z);
    }

    return 0;
}

int main(void) {
    double lambda = 632.8e-9; /* 632.8 нм */
    double slit_a = 0.2e-3;   /* 0.2 мм */
    double screen_w = 0.04;   /* 4 см екран */
    int n_screen = 200;

    double* intensity = (double*)malloc(sizeof(double) * n_screen);
    if (!intensity) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("=== Обчислення дифракції Фраунгофера (z = 2.0 м) ===\n");
    if (calc_fraunhofer_1d(lambda, slit_a, 500, screen_w, n_screen, 2.0, intensity) == 0) {
        printf("Центральна інтенсивність I(0): %.4e Вт/м²\n", intensity[n_screen / 2]);
        printf("Інтенсивність біля першого мінімуму: %.4e Вт/м²\n", intensity[n_screen / 2 + 15]);
    }

    printf("\n=== Обчислення дифракції Френеля (z = 0.08 м) ===\n");
    if (calc_fresnel_1d(lambda, slit_a, 500, screen_w, n_screen, 0.08, intensity) == 0) {
        printf("Центральна інтенсивність Френеля I(0): %.4e Вт/м²\n", intensity[n_screen / 2]);
    }

    free(intensity);
    return 0;
}
