#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    int mode_index;
    bool is_even;
    double u;
    double h;
    double q;
    double beta;
    double n_eff;
} WaveguideMode;

typedef struct {
    double n1;
    double n2;
    double d_um;
    double lambda_um;
    double k0;
    double V;
    int num_modes;
    WaveguideMode* modes;
} WaveguideSolver;

static double mode_equation(double u, double V, bool is_even) {
    double radius_sq = (V / 2.0) * (V / 2.0);
    double w = sqrt(radius_sq - u * u);
    if (is_even) {
        return u * tan(u) - w;
    } else {
        return -u * (1.0 / tan(u)) - w;
    }
}

static double solve_bisection(double low, double high, double V, bool is_even, double tol) {
    double mid = low;
    for (int iter = 0; iter < 100; ++iter) {
        mid = 0.5 * (low + high);
        if ((high - low) < tol) {
            break;
        }
        double f_mid = mode_equation(mid, V, is_even);
        double f_low = mode_equation(low, V, is_even);
        if (f_mid * f_low <= 0.0) {
            high = mid;
        } else {
            low = mid;
        }
    }
    return mid;
}

bool waveguide_solver_init(WaveguideSolver* solver, double n1, double n2, double d_um, double lambda_um) {
    if (n1 <= n2 || d_um <= 0.0 || lambda_um <= 0.0) {
        return false;
    }
    solver->n1 = n1;
    solver->n2 = n2;
    solver->d_um = d_um;
    solver->lambda_um = lambda_um;

    solver->k0 = 2.0 * M_PI / lambda_um;
    double NA = sqrt(n1 * n1 - n2 * n2);
    solver->V = solver->k0 * d_um * NA;

    solver->num_modes = (int)floor(solver->V / M_PI) + 1;
    solver->modes = (WaveguideMode*)malloc(solver->num_modes * sizeof(WaveguideMode));
    if (!solver->modes) {
        return false;
    }

    double tol = 1e-9;
    for (int m = 0; m < solver->num_modes; ++m) {
        bool is_even = (m % 2 == 0);
        double low = m * (M_PI / 2.0) + 1e-5;
        double high = (m + 1) * (M_PI / 2.0) - 1e-5;

        if (high > solver->V / 2.0) {
            high = solver->V / 2.0 - 1e-5;
        }

        double u_val = solve_bisection(low, high, solver->V, is_even, tol);
        double h_val = 2.0 * u_val / d_um;
        double q_val = 2.0 * sqrt((solver->V / 2.0) * (solver->V / 2.0) - u_val * u_val) / d_um;
        double beta_val = sqrt(solver->k0 * solver->k0 * n1 * n1 - h_val * h_val);

        solver->modes[m].mode_index = m;
        solver->modes[m].is_even = is_even;
        solver->modes[m].u = u_val;
        solver->modes[m].h = h_val;
        solver->modes[m].q = q_val;
        solver->modes[m].beta = beta_val;
        solver->modes[m].n_eff = beta_val / solver->k0;
    }
    return true;
}

void waveguide_solver_free(WaveguideSolver* solver) {
    if (solver && solver->modes) {
        free(solver->modes);
        solver->modes = NULL;
    }
}

int main(void) {
    WaveguideSolver solver;
    // Оптичний хвилевід: серцевина n1=1.50, оболонка n2=1.45, d=5.0 мкм, lambda=1.55 мкм
    if (waveguide_solver_init(&solver, 1.50, 1.45, 5.0, 1.55)) {
        printf("--- Результати розрахунку планарного хвилеводу (C) ---\n");
        printf("V-число: %.4f (Знайдено мод: %d)\n\n", solver.V, solver.num_modes);
        for (int i = 0; i < solver.num_modes; ++i) {
            printf("Мода TE%d (%s):\n", solver.modes[i].mode_index, solver.modes[i].is_even ? "Парна" : "Непарна");
            printf("  u = %.6f, h = %.6f 1/мкм, q = %.6f 1/мкм\n", solver.modes[i].u, solver.modes[i].h, solver.modes[i].q);
            printf("  beta = %.6f 1/мкм, n_eff = %.6f\n\n", solver.modes[i].beta, solver.modes[i].n_eff);
        }
        waveguide_solver_free(&solver);
    }
    return 0;
}
