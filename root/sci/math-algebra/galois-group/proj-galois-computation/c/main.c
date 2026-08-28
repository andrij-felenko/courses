#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

/* Типи груп Ґалуа для степенів n <= 4 */
typedef enum {
    GALOIS_UNKNOWN = 0,
    GALOIS_Z2,      /* n=2: Z_2 (порядок 2) */
    GALOIS_Z3,      /* n=3: A_3 = Z_3 (порядок 3) */
    GALOIS_S3,      /* n=3: S_3 (порядок 6) */
    GALOIS_Z4,      /* n=4: Z_4 (порядок 4) */
    GALOIS_V4,      /* n=4: V_4 = Z_2 x Z_2 (порядок 4) */
    GALOIS_D4,      /* n=4: D_4 (порядок 8) */
    GALOIS_A4,      /* n=4: A_4 (порядок 12) */
    GALOIS_S4       /* n=4: S_4 (порядок 24) */
} GaloisType;

/* Перевірка, чи є дійсне число точним квадратом раціонального (з урахуванням похибки) */
static bool is_rational_square(double val, double eps) {
    if (val < -eps) return false;
    if (fabs(val) < eps) return true;
    double root = sqrt(val);
    double nearest = round(root);
    return fabs(root - nearest) < eps;
}

/* Пошук раціональних коренів кубічного многочлена t^3 + A*t^2 + B*t + C = 0 */
static int find_rational_roots_cubic(double A, double B, double C, double roots[3], double eps) {
    int count = 0;
    /* Перевірка можливих цілих дільників вільного члена для цілих коефіцієнтів */
    int max_test = (int)fabs(C);
    if (max_test == 0) max_test = 20;
    if (max_test > 200) max_test = 200;

    for (int num = -max_test; num <= max_test; ++num) {
        for (int den = 1; den <= 8; ++den) {
            double t = (double)num / (double)den;
            double val = t * t * t + A * t * t + B * t + C;
            if (fabs(val) < eps) {
                bool exists = false;
                for (int i = 0; i < count; ++i) {
                    if (fabs(roots[i] - t) < eps) { exists = true; break; }
                }
                if (!exists && count < 3) {
                    roots[count++] = t;
                }
            }
        }
    }
    return count;
}

/* Обчислення групи Ґалуа многочлена 4-го степеня x^4 + a3*x^3 + a2*x^2 + a1*x + a0 */
GaloisType compute_galois_quartic(double a3, double a2, double a1, double a0) {
    double eps = 1e-7;

    /* Зведення до форми y^4 + p*y^2 + q*y + r */
    double p = a2 - 0.375 * a3 * a3;
    double q = a1 - 0.5 * a3 * a2 + 0.125 * a3 * a3 * a3;
    double r = a0 - 0.25 * a3 * a1 + 0.0625 * a3 * a3 * a2 - 0.01171875 * a3 * a3 * a3 * a3;

    /* Обчислення дискримінанта */
    double p2 = p * p, p3 = p2 * p, p4 = p2 * p2;
    double q2 = q * q, q4 = q2 * q2;
    double r2 = r * r, r3 = r2 * r;

    double disc = 256.0 * r3 - 128.0 * p2 * r2 + 144.0 * p * q2 * r
                  - 27.0 * q4 + 16.0 * p4 * r - 4.0 * p3 * q2;

    bool disc_is_sq = is_rational_square(disc, eps);

    /* Кубічна резольвента: t^3 + 2p*t^2 + (p^2 - 4r)*t - q^2 = 0 */
    double res_A = 2.0 * p;
    double res_B = p * p - 4.0 * r;
    double res_C = -q * q;

    double resolvent_roots[3];
    int num_roots = find_rational_roots_cubic(res_A, res_B, res_C, resolvent_roots, eps);

    printf("  [p = %.3f, q = %.3f, r = %.3f] Дискримінант = %.3f (%s)\n",
           p, q, r, disc, disc_is_sq ? "повний квадрат" : "не квадрат");
    printf("  Кубічна резольвента має %d рац. коренів\n", num_roots);

    if (num_roots == 0) {
        return disc_is_sq ? GALOIS_A4 : GALOIS_S4;
    } else if (num_roots >= 3) {
        return GALOIS_V4;
    } else {
        /* 1 раціональний корінь: розрізнення між D_4 та Z_4 */
        double theta = resolvent_roots[0];
        double test_val = (theta - p) * (theta - p) - 4.0 * r;
        if (is_rational_square(test_val * disc, eps)) {
            return GALOIS_Z4;
        }
        return GALOIS_D4;
    }
}

const char* galois_name(GaloisType type) {
    switch (type) {
        case GALOIS_Z2: return "Z_2 (порядок 2, циклічна, розв'язна)";
        case GALOIS_Z3: return "A_3 = Z_3 (порядок 3, циклічна, розв'язна)";
        case GALOIS_S3: return "S_3 (порядок 6, неабелева, розв'язна)";
        case GALOIS_Z4: return "Z_4 (порядок 4, циклічна, розв'язна)";
        case GALOIS_V4: return "V_4 = Z_2 x Z_2 (порядок 4, четвірна Клейна, розв'язна)";
        case GALOIS_D4: return "D_4 (порядок 8, група діедра квадрата, розв'язна)";
        case GALOIS_A4: return "A_4 (порядок 12, знакозмінна тетраедра, розв'язна)";
        case GALOIS_S4: return "S_4 (порядок 24, повна симетрична 4 коренів, розв'язна)";
        default:        return "Невідома група";
    }
}

int main(void) {
    printf("Обчислення груп Ґалуа многочленів 4-го степеня:\n\n");

    /* Тест 1: x^4 - 2 (очікується D_4) */
    printf("1. Многочлен f(x) = x^4 - 2:\n");
    GaloisType g1 = compute_galois_quartic(0, 0, 0, -2);
    printf("   => Група Ґалуа: %s\n\n", galois_name(g1));

    /* Тест 2: x^4 + 1 (очікується V_4) */
    printf("2. Многочлен f(x) = x^4 + 1:\n");
    GaloisType g2 = compute_galois_quartic(0, 0, 0, 1);
    printf("   => Група Ґалуа: %s\n\n", galois_name(g2));

    /* Тест 3: x^4 - 4x + 2 (очікується S_4) */
    printf("3. Многочлен f(x) = x^4 - 4x + 2:\n");
    GaloisType g3 = compute_galois_quartic(0, 0, -4, 2);
    printf("   => Група Ґалуа: %s\n\n", galois_name(g3));

    /* Тест 4: x^4 + x^3 + x^2 + x + 1 (циклотомічний, очікується Z_4) */
    printf("4. Многочлен f(x) = x^4 + x^3 + x^2 + x + 1:\n");
    GaloisType g4 = compute_galois_quartic(1, 1, 1, 1);
    printf("   => Група Ґалуа: %s\n\n", galois_name(g4));

    return 0;
}
