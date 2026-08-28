#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_DEGREE 16

/* Структура для представлення многочлена P(x) = coeffs[0]*x^n + ... + coeffs[n] */
typedef struct {
    int degree;
    double coeffs[MAX_DEGREE + 1];
} Polynomial;

/* Результат знаходження коренів кубічного рівняння */
typedef struct {
    int root_count;
    double roots[3];
} CubicRoots;

/*
 * Обчислення коефіцієнтів многочлена за заданими коренями (симетрична згортка)
 * Вхід: масив roots довжини n
 * Вихід: поліном P(x) = (x - r_1)...(x - r_n) зі старшим коефіцієнтом coeffs[0] = 1.0
 */
Polynomial poly_from_roots(const double *roots, int n) {
    Polynomial p;
    p.degree = n;
    
    for (int i = 0; i <= n; i++) {
        p.coeffs[i] = 0.0;
    }
    p.coeffs[0] = 1.0;

    for (int i = 0; i < n; i++) {
        double r = roots[i];
        for (int j = i + 1; j > 0; j--) {
            p.coeffs[j] = p.coeffs[j] - r * p.coeffs[j - 1];
        }
    }

    return p;
}

/*
 * Перетворення сум степенів s_1, ..., s_n на елементарні многочлени e_1, ..., e_n
 * за рекурентними тотожностями Ньютона — Жирара.
 */
void power_sums_to_elementary(const double *s, double *e, int n) {
    e[0] = 1.0;
    for (int k = 1; k <= n; k++) {
        double sum = 0.0;
        double sign = 1.0;
        
        for (int j = 1; j < k; j++) {
            sum += sign * e[k - j] * s[j - 1];
            sign = -sign;
        }
        
        sum += sign * s[k - 1];
        e[k] = sum / (double)k;
    }
}

/*
 * Розв'язання дійсного кубічного рівняння t^3 - e1*t^2 + e2*t - e3 = 0
 * Тригонометричний метод Вієта для випадку трьох дійсних коренів.
 */
CubicRoots solve_cubic_vieta(double e1, double e2, double e3) {
    CubicRoots res;
    res.root_count = 0;

    /* Зведення до неповного кубічного рівняння y^3 + p*y + q = 0 підстановкою t = y + e1/3 */
    double shift = e1 / 3.0;
    double p = e2 - (e1 * e1) / 3.0;
    double q = -e3 + (e1 * e2) / 3.0 - (2.0 * e1 * e1 * e1) / 27.0;

    double disc = (q * q) / 4.0 + (p * p * p) / 27.0;

    if (disc <= 1e-12) {
        /* Три дійсні корені (casus irreducibilis) */
        double r = sqrt(- (p * p * p) / 27.0);
        double cos_val = -q / (2.0 * r);
        if (cos_val > 1.0) cos_val = 1.0;
        if (cos_val < -1.0) cos_val = -1.0;
        double phi = acos(cos_val);
        double factor = 2.0 * cbrt(r);

        res.roots[0] = factor * cos(phi / 3.0) + shift;
        res.roots[1] = factor * cos((phi + 2.0 * M_PI) / 3.0) + shift;
        res.roots[2] = factor * cos((phi + 4.0 * M_PI) / 3.0) + shift;
        res.root_count = 3;
    } else {
        /* Один дійсний корінь за формулою Кардано */
        double u = cbrt(-q / 2.0 + sqrt(disc));
        double v = cbrt(-q / 2.0 - sqrt(disc));
        res.roots[0] = (u + v) + shift;
        res.root_count = 1;
    }

    return res;
}

int main(void) {
    /* Демонстрація 1: Синтез многочлена за заданими коренями */
    double known_roots[3] = {1.0, 2.0, 3.0};
    Polynomial poly = poly_from_roots(known_roots, 3);

    printf("Синтезований многочлен за коренями {1, 2, 3}:\n");
    printf("P(x) = x^3 + (%.1f)x^2 + (%.1f)x + (%.1f)\n\n",
           poly.coeffs[1], poly.coeffs[2], poly.coeffs[3]);

    /* Демонстрація 2: Розв'язання нелінійної системи:
     * x + y + z = 6
     * x^2 + y^2 + z^2 = 14
     * x^3 + y^3 + z^3 = 36
     */
    double power_sums[3] = {6.0, 14.0, 36.0};
    double e[4] = {1.0, 0.0, 0.0, 0.0};

    power_sums_to_elementary(power_sums, e, 3);

    printf("Обчислені коефіцієнти Вієта за сумами степенів:\n");
    printf("e1 = %.2f, e2 = %.2f, e3 = %.2f\n\n", e[1], e[2], e[3]);

    CubicRoots roots = solve_cubic_vieta(e[1], e[2], e[3]);
    printf("Знайдені корені системи (базовий розв'язок):\n");
    for (int i = 0; i < roots.root_count; i++) {
        printf("t_%d = %.4f\n", i + 1, roots.roots[i]);
    }

    return 0;
}
