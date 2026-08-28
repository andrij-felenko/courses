/* C реалізація ітераційного солуера Швінгера-Дайсона */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

typedef struct {
    int N_pts;
    double beta;
    double J;
    double alpha;
    double complex *G_omega;
    double complex *Sigma_omega;
    double *G_tau;
    double *Sigma_tau;
} SYKSolverC;

SYKSolverC* syk_solver_create(int N_pts, double beta, double J, double alpha) {
    SYKSolverC *s = (SYKSolverC*)malloc(sizeof(SYKSolverC));
    s->N_pts = N_pts;
    s->beta = beta;
    s->J = J;
    s->alpha = alpha;
    s->G_omega = (double complex*)malloc(sizeof(double complex) * N_pts);
    s->Sigma_omega = (double complex*)malloc(sizeof(double complex) * N_pts);
    s->G_tau = (double*)malloc(sizeof(double) * N_pts);
    s->Sigma_tau = (double*)malloc(sizeof(double) * N_pts);

    /* Ініціалізація вільним пропагатором */
    for (int n = 0; n < N_pts; n++) {
        double omega_n = (2 * n + 1 - N_pts) * PI / beta;
        s->G_omega[n] = 1.0 / (I * omega_n);
        s->Sigma_omega[n] = 0.0 + 0.0 * I;
    }
    return s;
}

void syk_solver_free(SYKSolverC *s) {
    if (!s) return;
    free(s->G_omega);
    free(s->Sigma_omega);
    free(s->G_tau);
    free(s->Sigma_tau);
    free(s);
}

void syk_solver_step(SYKSolverC *s) {
    int M = s->N_pts;
    double dt = s->beta / M;

    /* Спрощене перетворення Фур'є G(omega) -> G(tau) */
    for (int k = 0; k < M; k++) {
        double tau = (k + 0.5) * dt;
        double complex g_val = 0.0;
        for (int n = 0; n < M; n++) {
            double omega_n = (2 * n + 1 - M) * PI / s->beta;
            g_val += s->G_omega[n] * cexp(-I * omega_n * tau) / s->beta;
        }
        s->G_tau[k] = creal(g_val);
        /* Самоенергія q=4: Sigma(tau) = J^2 * [G(tau)]^3 */
        s->Sigma_tau[k] = s->J * s->J * pow(s->G_tau[k], 3);
    }

    /* Перетворення Фур'є Sigma(tau) -> Sigma(omega) та оновлення G */
    for (int n = 0; n < M; n++) {
        double omega_n = (2 * n + 1 - M) * PI / s->beta;
        double complex sig_val = 0.0;
        for (int k = 0; k < M; k++) {
            double tau = (k + 0.5) * dt;
            sig_val += s->Sigma_tau[k] * cexp(I * omega_n * tau) * dt;
        }
        s->Sigma_omega[n] = sig_val;

        /* Демпфоване оновлення G_new */
        double complex G_new = 1.0 / (I * omega_n - s->Sigma_omega[n]);
        s->G_omega[n] = (1.0 - s->alpha) * s->G_omega[n] + s->alpha * G_new;
    }
}

int main(void) {
    int N_pts = 64;
    double beta = 10.0;
    double J = 1.0;
    double alpha = 0.2;

    SYKSolverC *solver = syk_solver_create(N_pts, beta, J, alpha);
    printf("Розпочато чисельний розв'язок рівнянь Швінгера-Дайсона (C)...\n");

    for (int iter = 0; iter < 50; iter++) {
        syk_solver_step(solver);
    }

    printf("Розв'язок успішно досягнуто! G(tau=beta/2) = %.6f\n", solver->G_tau[N_pts / 2]);
    syk_solver_free(solver);
    return 0;
}
