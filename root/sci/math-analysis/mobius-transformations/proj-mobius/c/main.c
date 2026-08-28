#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef double complex Complex;

/* Структура для опису перетворення Мьобіуса: f(z) = (a*z + b) / (c*z + d) */
typedef struct {
    Complex a;
    Complex b;
    Complex c;
    Complex d;
} MobiusTransform;

/* Режим класифікації перетворення */
typedef enum {
    MOBIUS_PARABOLIC,
    MOBIUS_ELLIPTIC,
    MOBIUS_HYPERBOLIC,
    MOBIUS_LOXODROMIC
} MobiusType;

/* Створення нового перетворення */
MobiusTransform mobius_create(Complex a, Complex b, Complex c, Complex d) {
    MobiusTransform m;
    m.a = a; m.b = b; m.c = c; m.d = d;
    return m;
}

/* Обчислення визначника ad - bc */
Complex mobius_det(MobiusTransform m) {
    return m.a * m.d - m.b * m.c;
}

/* Нормалізація коефіцієнтів так, щоб det = 1 */
MobiusTransform mobius_normalize(MobiusTransform m) {
    Complex det = mobius_det(m);
    Complex denom = csqrt(det);
    if (cabs(denom) < 1e-15) {
        fprintf(stderr, "Помилка: Вироджене перетворення Мьобіуса (det = 0)\n");
        return m;
    }
    return mobius_create(m.a / denom, m.b / denom, m.c / denom, m.d / denom);
}

/* Композиція двох перетворень (m1 o m2)(z) = m1(m2(z)) — множення матриць */
MobiusTransform mobius_compose(MobiusTransform m1, MobiusTransform m2) {
    Complex a = m1.a * m2.a + m1.b * m2.c;
    Complex b = m1.a * m2.b + m1.b * m2.d;
    Complex c = m1.c * m2.a + m1.d * m2.c;
    Complex d = m1.c * m2.b + m1.d * m2.d;
    return mobius_create(a, b, c, d);
}

/* Обернене перетворення M^(-1) */
MobiusTransform mobius_inverse(MobiusTransform m) {
    MobiusTransform norm = mobius_normalize(m);
    return mobius_create(norm.d, -norm.b, -norm.c, norm.a);
}

/* Обчислення f(z) для точки z */
Complex mobius_eval(MobiusTransform m, Complex z, bool *is_infinity) {
    Complex denom = m.c * z + m.d;
    if (cabs(denom) < 1e-12) {
        if (is_infinity) *is_infinity = true;
        return CMPLX(INFINITY, INFINITY);
    }
    if (is_infinity) *is_infinity = false;
    return (m.a * z + m.b) / denom;
}

/* Обчислення нерухомих точок c*z^2 + (d - a)*z - b = 0 */
int mobius_fixed_points(MobiusTransform m, Complex out_fixed[2]) {
    MobiusTransform n = mobius_normalize(m);
    if (cabs(n.c) < 1e-12) {
        if (cabs(n.a - n.d) < 1e-12) {
            return 0;
        }
        out_fixed[0] = n.b / (n.d - n.a);
        out_fixed[1] = CMPLX(INFINITY, INFINITY);
        return 1;
    }

    Complex A = n.c;
    Complex B = n.d - n.a;
    Complex C = -n.b;
    Complex disc = B * B - 4.0 * A * C;
    Complex sqrt_disc = csqrt(disc);

    out_fixed[0] = (-B + sqrt_disc) / (2.0 * A);
    out_fixed[1] = (-B - sqrt_disc) / (2.0 * A);
    return 2;
}

/* Класифікація за квадрантом сліду Tr(M)^2 */
MobiusType mobius_classify(MobiusTransform m) {
    MobiusTransform n = mobius_normalize(m);
    Complex tr = n.a + n.d;
    Complex tr2 = tr * tr;

    double im_part = cimag(tr2);
    double re_part = creal(tr2);

    if (fabs(im_part) < 1e-9) {
        if (fabs(re_part - 4.0) < 1e-9) return MOBIUS_PARABOLIC;
        if (re_part >= 0.0 && re_part < 4.0) return MOBIUS_ELLIPTIC;
        if (re_part > 4.0) return MOBIUS_HYPERBOLIC;
    }
    return MOBIUS_LOXODROMIC;
}

int main(void) {
    MobiusTransform m = mobius_create(1.0, -1.0, 1.0, 1.0);
    MobiusTransform norm = mobius_normalize(m);

    printf("--- Тест перетворення Мьобіуса (C) ---\n");
    Complex det = mobius_det(norm);
    printf("Визначник після нормалізації: %.4f + %.4fi\n", creal(det), cimag(det));

    Complex z_test = 2.0 + 3.0 * I;
    bool is_inf = false;
    Complex w_test = mobius_eval(norm, z_test, &is_inf);
    printf("f(2 + 3i) = %.4f + %.4fi\n", creal(w_test), cimag(w_test));

    Complex fixed[2];
    int n_fix = mobius_fixed_points(norm, fixed);
    printf("Кількість нерухомих точок: %d\n", n_fix);
    for (int i = 0; i < n_fix; ++i) {
        printf("  z_%d = %.4f + %.4fi\n", i + 1, creal(fixed[i]), cimag(fixed[i]));
    }

    MobiusType type = mobius_classify(norm);
    const char *type_names[] = {"Параболічне", "Еліптичне", "Гіперболічне", "Локсодромне"};
    printf("Тип перетворення: %s\n", type_names[type]);

    return 0;
}
