#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define KB_EV 8.617333262e-5  /* Стала Больцмана в еВ/К */
#define ELEC_CHARGE 1.602176634e-19
#define EPS0 8.854187812e-12

typedef struct {
    double temp_k;        /* Температура в Кельвінах */
    double rel_perm;      /* Відносна діелектрична проникність */
    double n0_m3;         /* Концентрація носіїв у м⁻³ */
    double debye_m;       /* Обчислена дебаївська довжина */
} DebyeParams;

typedef struct {
    int num_points;
    double grid_step;
    double *x_coords;
    double *potential_v;
} SimulationResult;

/* Обчислення радіуса Дебая */
double compute_debye_length(double temp_k, double rel_perm, double n0_m3) {
    double eps = rel_perm * EPS0;
    double vt = (KB_EV * temp_k); /* у вольтах */
    return sqrt((eps * vt) / (2.0 * n0_m3 * ELEC_CHARGE));
}

/* Ініціалізація симуляції */
int run_debye_simulation(DebyeParams params, double phi0_v, double x_max_m, 
                         int N, double tol, SimulationResult *out_res) {
    if (N < 3 || params.debye_m <= 0.0 || out_res == NULL) {
        return -1;
    }

    double *x = (double *)malloc(sizeof(double) * N);
    double *phi = (double *)malloc(sizeof(double) * N);
    if (!x || !phi) {
        free(x);
        free(phi);
        return -2;
    }

    double h = x_max_m / (N - 1);
    double vt = KB_EV * params.temp_k;
    double inv_ld2 = 1.0 / (params.debye_m * params.debye_m);

    /* Початкові умови: лінійний спад */
    for (int i = 0; i < N; ++i) {
        x[i] = i * h;
        phi[i] = phi0_v * exp(-x[i] / params.debye_m);
    }
    phi[0] = phi0_v;
    phi[N - 1] = 0.0;

    /* Ітераційний процес релаксації Гаусса — Зайделя */
    int max_iter = 10000;
    double omega = 0.5; /* Коефіцієнт релаксації */

    for (int iter = 0; iter < max_iter; ++iter) {
        double max_diff = 0.0;
        for (int i = 1; i < N - 1; ++i) {
            double rhs = inv_ld2 * vt * sinh(phi[i] / vt);
            double phi_new = 0.5 * (phi[i + 1] + phi[i - 1] - h * h * rhs);
            double phi_relaxed = (1.0 - omega) * phi[i] + omega * phi_new;

            double diff = fabs(phi_relaxed - phi[i]);
            if (diff > max_diff) {
                max_diff = diff;
            }
            phi[i] = phi_relaxed;
        }

        if (max_diff < tol) {
            break;
        }
    }

    out_res->num_points = N;
    out_res->grid_step = h;
    out_res->x_coords = x;
    out_res->potential_v = phi;
    return 0;
}

void free_simulation_result(SimulationResult *res) {
    if (res) {
        free(res->x_coords);
        free(res->potential_v);
        res->x_coords = NULL;
        res->potential_v = NULL;
    }
}
