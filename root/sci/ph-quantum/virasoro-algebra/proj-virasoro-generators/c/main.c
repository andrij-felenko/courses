#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double c;
    int max_mode;
} VirasoroAlgebra;

double virasoro_central_term(double c, int n, int m) {
    if (n + m != 0) {
        return 0.0;
    }
    return (c / 12.0) * (double)(n * n * n - n);
}

bool check_virasoro_jacobi(double c, int k, int m, int n) {
    double t1 = (double)(m - n) * virasoro_central_term(c, k, m + n);
    double t2 = (double)(n - k) * virasoro_central_term(c, m, n + k);
    double t3 = (double)(k - m) * virasoro_central_term(c, n, k + m);
    double sum = t1 + t2 + t3;
    return fabs(sum) < 1e-9;
}

double compute_kac_det_level2(double c, double h) {
    double m11 = 4.0 * h + c / 2.0;
    double m12 = 6.0 * h;
    double m21 = 6.0 * h;
    double m22 = 4.0 * h * (2.0 * h + 1.0);
    return m11 * m22 - m12 * m21;
}

int main(void) {
    double c = 26.0;
    printf("C verification of Virasoro algebra (c = %.1f):\n", c);
    
    bool ok = check_virasoro_jacobi(c, 3, -7, 4);
    printf("Jacobi identity for (3, -7, 4): %s\n", ok ? "PASSED" : "FAILED");
    
    double h = 0.0625; // h = 1/16
    double det2 = compute_kac_det_level2(0.5, h);
    printf("Kac determinant level 2 (c=0.5, h=1/16): %.6f\n", det2);
    
    return 0;
}
