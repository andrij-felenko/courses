#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#define PI 3.14159265358979323846

/* Обчислення дискретного логарифма у F_p за основою g=3 */
static int dlog_base3(int x, int p) {
    if (x % p == 0) return -1;
    int val = x % p;
    int curr = 1;
    for (int k = 0; k < p - 1; k++) {
        if (curr == val) return k;
        curr = (curr * 3) % p;
    }
    return 0;
}

/* Мультиплікативний кубічний характер */
static double complex chi_base(int x, int p) {
    if (x % p == 0) return 0.0 + 0.0 * I;
    int k = dlog_base3(x, p);
    double angle = 2.0 * PI * (k % 3) / 3.0;
    return cpow(E, I * angle);
}

/* Адитивний характер */
static double complex psi_base(int x, int p) {
    double angle = 2.0 * PI * (x % p) / p;
    return ccos(angle) + I * csin(angle);
}

int main(void) {
    const int p = 7;
    const int s = 2;

    /* 1. Обчислюємо базову суму Гаусса у F_7 */
    double complex g_small = 0.0 + 0.0 * I;
    for (int x = 1; x < p; x++) {
        g_small += chi_base(x, p) * psi_base(x, p);
    }

    printf("C [F_7]  Base Gauss sum g(chi, psi) = %.5f + %.5fi\n", 
           creal(g_small), cimag(g_small));
    printf("C [F_7]  Modulus |g| = %.5f (Expected: %.5f)\n", 
           cabs(g_small), sqrt(p));

    /* 2. Обчислюємо підняту суму у F_49 через Норму та Слід */
    double complex g_lifted = 0.0 + 0.0 * I;
    for (int u = 0; u < p; u++) {
        for (int v = 0; v < p; v++) {
            if (u == 0 && v == 0) continue;
            int norm_val = (u * u + v * v) % p;
            int trace_val = (2 * u) % p;
            g_lifted += chi_base(norm_val, p) * psi_base(trace_val, p);
        }
    }

    printf("\nC [F_49] Lifted Gauss sum g(chi', psi') = %.5f + %.5fi\n", 
           creal(g_lifted), cimag(g_lifted));
    printf("C [F_49] Modulus |g_lifted| = %.5f (Expected: %d.00000)\n", 
           cabs(g_lifted), p);

    /* 3. Перевірка формули підйому: g(chi', psi') = (-1)^(s-1) * g_small^2 */
    double complex predicted = -1.0 * cpow(g_small, (double)s);
    double diff = cabs(g_lifted - predicted);

    printf("\nC Predicted (-1)^(s-1) * g^s = %.5f + %.5fi\n", 
           creal(predicted), cimag(predicted));
    printf("C Diff = %.9e\n", diff);

    if (diff < 1e-7) {
        printf("C Verification SUCCESS!\n");
    } else {
        printf("C Verification FAILED!\n");
    }

    return 0;
}
