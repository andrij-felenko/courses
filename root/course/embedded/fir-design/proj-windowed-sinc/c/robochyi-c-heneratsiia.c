#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <math.h>      // sinf, cosf, sqrtf, powf, log10f, fabsf

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Який вікном обрізати ідеальний sinc.
typedef enum {
    WIN_HAMMING,    // фіксоване ~53 дБ — робочий стандарт
    WIN_KAISER      // налаштовне через beta — точно під задане As
} WindowKind;

// ── Модифікована функція Бесселя I0(x) рядом (відношення доданків) ──────────
// Без факторіалів і степенів: кожен доданок із попереднього. Збігається
// блискавично; 30 доданків покривають будь-яке розумне beta з запасом.
static double bessel_i0(double x)
{
    double term = 1.0;          // t_0 = 1
    double sum  = 1.0;          // часткова сума ряду
    double half_x_sq = (x * 0.5) * (x * 0.5);   // (x/2)^2 — спільний множник
    for (int k = 1; k < 30; ++k) {
        term *= half_x_sq / ((double)k * (double)k);   // t_k = t_{k-1}·(x/2)²/k²
        sum  += term;
        if (term < sum * 1e-12) break;     // доданок мізерний — далі марно
    }
    return sum;
}
