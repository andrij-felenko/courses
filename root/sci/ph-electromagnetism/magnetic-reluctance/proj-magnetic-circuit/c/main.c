#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define MU0 (4.0 * M_PI * 1e-7)

typedef struct {
    double k1;
    double k2;
    double k3;
    double b_sat;
} CoreMaterial;

typedef struct {
    double b_field;
    double flux;
    double reluctance_core;
    double reluctance_gap;
    double total_reluctance;
    double inductance;
    int iterations;
    bool converged;
} MagneticResult;

static double h_field(const CoreMaterial* mat, double b) {
    return (mat->k1 * exp(mat->k2 * b * b) + mat->k3) * b;
}

static double dh_db(const CoreMaterial* mat, double b) {
    double b2 = b * b;
    double exp_val = exp(mat->k2 * b2);
    return mat->k1 * exp_val * (1.0 + 2.0 * mat->k2 * b2) + mat->k3;
}

bool solve_magnetic_circuit(double l_core, double l_gap, double area,
                            int turns, double current, const CoreMaterial* mat,
                            MagneticResult* result) {
    double mmf = turns * current;
    double b = 0.1;
    const int max_iter = 100;
    const double tol = 1e-7;

    for (int iter = 0; iter < max_iter; iter++) {
        double h = h_field(mat, b);
        double f_val = h * l_core + (b / MU0) * l_gap - mmf;
        double df_val = dh_db(mat, b) * l_core + l_gap / MU0;

        double delta = f_val / df_val;
        b -= delta;

        if (b < 1e-6) b = 1e-6;

        if (fabs(delta) < tol) {
            result->b_field = b;
            result->flux = b * area;
            result->reluctance_gap = l_gap / (MU0 * area);
            result->reluctance_core = (h_field(mat, b) * l_core) / result->flux;
            result->total_reluctance = result->reluctance_core + result->reluctance_gap;
            result->inductance = (turns * turns) / result->total_reluctance;
            result->iterations = iter + 1;
            result->converged = true;
            return true;
        }
    }
    result->converged = false;
    return false;
}

int main(void) {
    CoreMaterial ferrite = { .k1 = 4.5, .k2 = 3.8, .k3 = 120.0, .b_sat = 0.42 };
    MagneticResult res;

    if (solve_magnetic_circuit(0.114, 0.001, 2.11e-4, 30, 8.0, &ferrite, &res)) {
        printf("B = %.4f T\n", res.b_field);
        printf("Flux = %.2f uWb\n", res.flux * 1e6);
        printf("Rm_core = %.1f A*t/Wb\n", res.reluctance_core);
        printf("Rm_gap  = %.1f A*t/Wb\n", res.reluctance_gap);
        printf("L = %.2f uH\n", res.inductance * 1e6);
    } else {
        printf("Помилка: алгоритм не збігся.\n");
    }
    return 0;
}
