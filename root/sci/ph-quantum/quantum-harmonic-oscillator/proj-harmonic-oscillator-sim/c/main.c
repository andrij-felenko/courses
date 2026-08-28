#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Опис структури чисельного розв'язувача квантового осцилятора мовою C */
typedef struct {
    int N;
    double h;
    double* xi;
    double* d;  /* діагональні елементи */
    double* e;  /* позадіагональні елементи */
    double* eigenvalues;
} QHO_SolverC;

QHO_SolverC* qho_create(double L, int N) {
    QHO_SolverC* solver = (QHO_SolverC*)malloc(sizeof(QHO_SolverC));
    if (!solver) return NULL;

    solver->N = N;
    solver->h = (2.0 * L) / (N - 1);
    solver->xi = (double*)malloc(N * sizeof(double));
    solver->d = (double*)malloc(N * sizeof(double));
    solver->e = (double*)malloc((N - 1) * sizeof(double));
    solver->eigenvalues = (double*)malloc(N * sizeof(double));

    if (!solver->xi || !solver->d || !solver->e || !solver->eigenvalues) {
        free(solver->xi); free(solver->d); free(solver->e); free(solver->eigenvalues);
        free(solver);
        return NULL;
    }

    double h2 = solver->h * solver->h;
    for (int i = 0; i < N; i++) {
        solver->xi[i] = -L + i * solver->h;
        solver->d[i] = 1.0 / h2 + 0.5 * solver->xi[i] * solver->xi[i];
        if (i < N - 1) {
            solver->e[i] = -0.5 / h2;
        }
    }
    return solver;
}

void qho_free(QHO_SolverC* solver) {
    if (!solver) return;
    free(solver->xi);
    free(solver->d);
    free(solver->e);
    free(solver->eigenvalues);
    free(solver);
}

/* Бісекційний метод з послідовністю Штурма для тридіагональних матриць */
int qho_solve_eigenvalues(QHO_SolverC* solver, int num_states) {
    for (int k = 0; k < num_states; k++) {
        double low = 0.0;
        double high = k + 2.5;

        for (int iter = 0; iter < 60; iter++) {
            double mid = 0.5 * (low + high);
            int count = 0;
            double p = solver->d[0] - mid;
            if (p < 0) count++;

            for (int i = 1; i < solver->N; i++) {
                p = (solver->d[i] - mid) - (solver->e[i-1] * solver->e[i-1]) / (p == 0 ? 1e-14 : p);
                if (p < 0) count++;
            }

            if (count <= k) {
                low = mid;
            } else {
                high = mid;
            }
        }
        solver->eigenvalues[k] = 0.5 * (low + high);
    }
    return 0;
}

int main(void) {
    double L = 5.0;
    int N = 1000;
    QHO_SolverC* solver = qho_create(L, N);

    if (!solver) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    qho_solve_eigenvalues(solver, 5);

    printf("Результати обчислення власних значень (C реалізація):\n");
    for (int n = 0; n < 5; n++) {
        printf("n = %d: E_calc = %.6f, E_exact = %.1f\n", n, solver->eigenvalues[n], n + 0.5);
    }

    qho_free(solver);
    return 0;
}
