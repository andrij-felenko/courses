#include <stdio.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

static int dlog_gen3(int x, int p) {
    if (x % p == 0) return -1;
    int val = x % p, curr = 1;
    for (int k = 0; k < p - 1; k++) {
        if (curr == val) return k;
        curr = (curr * 3) % p;
    }
    return 0;
}

int main(void) {
    const int p = 7;
    const int m = 3;

    /* Обчислення Лівої частини: LHS = ∏_{a=0}^{2} g(χ · θᵃ, ψ) */
    double complex lhs = 1.0 + 0.0 * I;
    for (int a = 0; a < m; a++) {
        double complex g_shift = 0.0 + 0.0 * I;
        for (int x = 1; x < p; x++) {
            int k = dlog_gen3(x, p);
            double complex chi_val = cpow(E, I * 2.0 * PI * k / 6.0);
            double complex theta_val = cpow(E, I * 2.0 * PI * ((k * a) % 3) / 3.0);
            double complex psi_val = ccos(2.0 * PI * x / p) + I * csin(2.0 * PI * x / p);
            g_shift += chi_val * theta_val * psi_val;
        }
        lhs *= g_shift;
    }

    /* Обчислення Правої частини: RHS = χ(6) * g(χ³, ψ) * g(θ, ψ) * g(θ², ψ) */
    double complex chi_6 = cpow(E, I * 2.0 * PI * dlog_gen3(6, p) / 6.0); // χ(6) = -1
    
    double complex g_chi3 = 0.0 + 0.0 * I;
    for (int x = 1; x < p; x++) {
        int k = dlog_gen3(x, p);
        double complex chi3_val = cpow(E, I * 2.0 * PI * ((k * 3) % 6) / 6.0);
        double complex psi_val = ccos(2.0 * PI * x / p) + I * csin(2.0 * PI * x / p);
        g_chi3 += chi3_val * psi_val;
    }

    double complex prod_theta = 1.0 + 0.0 * I;
    for (int a = 1; a < m; a++) {
        double complex g_th = 0.0 + 0.0 * I;
        for (int x = 1; x < p; x++) {
            int k = dlog_gen3(x, p);
            double complex th_val = cpow(E, I * 2.0 * PI * ((k * a) % 3) / 3.0);
            double complex psi_val = ccos(2.0 * PI * x / p) + I * csin(2.0 * PI * x / p);
            g_th += th_val * psi_val;
        }
        prod_theta *= g_th;
    }

    double complex rhs = chi_6 * g_chi3 * prod_theta;
    double diff = cabs(lhs - rhs);

    printf("C Multiplicative LHS = %.5f + %.5fi\n", creal(lhs), cimag(lhs));
    printf("C Multiplicative RHS = %.5f + %.5fi\n", creal(rhs), cimag(rhs));
    printf("C Diff = %.9e\n", diff);

    return 0;
}
