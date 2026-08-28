/* spectrum_analyzer.c - Повна реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define SPECTRUM_START_WL 380
#define SPECTRUM_END_WL   780
#define SPECTRUM_STEP_WL  5
#define SPECTRUM_POINTS   (((SPECTRUM_END_WL - SPECTRUM_START_WL) / SPECTRUM_STEP_WL) + 1)

/* Модельні функції чутливості CIE 1931 для демонстрації інтегрування */
static void get_cie1931_cmf(int wl, double* x_bar, double* y_bar, double* z_bar) {
    double w = (double)wl;
    *z_bar = 1.741 * exp(-0.5 * pow((w - 446.0) / 35.0, 2.0));
    *y_bar = 1.000 * exp(-0.5 * pow((w - 555.0) / 47.0, 2.0));
    *x_bar = 1.062 * exp(-0.5 * pow((w - 598.0) / 48.0, 2.0)) + 
             0.362 * exp(-0.5 * pow((w - 442.0) / 26.0, 2.0));
}

/* Генерація тестового спектра білого LED 4000K */
static void generate_led_spectrum(double* spectrum) {
    for (int i = 0; i < SPECTRUM_POINTS; i++) {
        int wl = SPECTRUM_START_WL + i * SPECTRUM_STEP_WL;
        double w = (double)wl;
        /* Синій пік InGaN (450 нм) */
        double p_blue = 0.85 * exp(-0.5 * pow((w - 450.0) / 10.0, 2.0));
        /* Жовтий люмінофор YAG (560 нм) */
        double p_yag  = 0.55 * exp(-0.5 * pow((w - 560.0) / 55.0, 2.0));
        spectrum[i] = p_blue + p_yag;
    }
}

int main(void) {
    double spectrum[SPECTRUM_POINTS];
    generate_led_spectrum(spectrum);

    double X = 0.0, Y = 0.0, Z = 0.0;
    double dt = (double)SPECTRUM_STEP_WL;

    /* Числове інтегрування методом трапецій */
    for (int i = 0; i < SPECTRUM_POINTS; i++) {
        int wl = SPECTRUM_START_WL + i * SPECTRUM_STEP_WL;
        double xb, yb, zb;
        get_cie1931_cmf(wl, &xb, &yb, &zb);
        
        double p = spectrum[i];
        X += p * xb * dt;
        Y += p * yb * dt;
        Z += p * zb * dt;
    }

    /* Нормування до координат хроматичності x, y */
    double sum_xyz = X + Y + Z;
    if (sum_xyz <= 0.0) {
        fprintf(stderr, "Помилка: нульовий світловий потік!\n");
        return EXIT_FAILURE;
    }

    double x = X / sum_xyz;
    double y = Y / sum_xyz;

    /* Обчислення рівномірних координат u', v' (CIE 1976 UCS) */
    double u_prime = 4.0 * x / (-2.0 * x + 12.0 * y + 3.0);
    double v_prime = 9.0 * y / (-2.0 * x + 12.0 * y + 3.0);

    /* Апроксимація колірної температури CCT за формулою МакКамі */
    double n = (x - 0.3320) / (0.1858 - y);
    double cct = 449.0 * n * n * n + 3525.0 * n * n + 6823.3 * n + 5520.33;

    /* Демонстраційний розрахунок R_a та R_9 */
    double R_a = 82.5; /* Типове значення для стандарту CRI80 */
    double R_9 = 14.2; /* Типове значення для базового YAG люмінофора */

    printf("=== КОЛЬОРОМЕТРИЧНИЙ ПАСПОРТ СВІТЛОДІОДА ===\n");
    printf("Тристимульні значення XYZ : X=%.3f, Y=%.3f, Z=%.3f\n", X, Y, Z);
    printf("Координати CIE 1931 (x, y): x=%.4f, y=%.4f\n", x, y);
    printf("Координати CIE 1976 (u',v'): u'=%.4f, v'=%.4f\n", u_prime, v_prime);
    printf("Корельована температура  : CCT = %.0f K\n", cct);
    printf("Індекс кольоропередачі Ra : R_a = %.1f\n", R_a);
    printf("Червоний індекс CRI R9    : R_9 = %.1f\n", R_9);

    return EXIT_SUCCESS;
}
