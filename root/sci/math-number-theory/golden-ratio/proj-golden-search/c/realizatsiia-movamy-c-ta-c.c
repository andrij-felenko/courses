#include <stdio.h>
#include <math.h>

/* Константа inv_phi = (sqrt(5) - 1) / 2 */
#define INV_PHI 0.61803398874989484820

typedef double (*target_func_t)(double);

/*
 * Знаходить мінімум унімодальної функції func на інтервалі [a, b] з точністю eps.
 * Повертає абсцису знайденого мінімуму.
 */
double golden_section_search(target_func_t func, double a, double b, double eps, int *eval_count) {
    double x1 = b - INV_PHI * (b - a);
    double x2 = a + INV_PHI * (b - a);
    double f1 = func(x1);
    double f2 = func(x2);
    
    int evals = 2;

    while (fabs(b - a) > eps) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = b - INV_PHI * (b - a);
            f1 = func(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = a + INV_PHI * (b - a);
            f2 = func(x2);
        }
        evals++;
    }

    if (eval_count) {
        *eval_count = evals;
    }

    return (a + b) / 2.0;
}

/* Приклад: f(x) = (x - 3)^2 + 2, мінімум у x = 3.0 */
static double sample_function(double x) {
    return (x - 3.0) * (x - 3.0) + 2.0;
}

int main(void) {
    double a = 0.0, b = 10.0, eps = 1e-7;
    int evals = 0;
    
    double min_x = golden_section_search(sample_function, a, b, eps, &evals);
    
    printf("C Result: min_x = %.8f, f(min_x) = %.8f (evals = %d)\n", 
           min_x, sample_function(min_x), evals);
    
    return 0;
}
