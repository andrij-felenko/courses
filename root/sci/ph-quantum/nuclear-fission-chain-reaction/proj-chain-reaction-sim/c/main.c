#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_GROUPS 6

/* Ядерно-фізичні константи для 235U (теплові нейтрони) */
typedef struct {
    double beta[NUM_GROUPS];
    double lambda[NUM_GROUPS];
    double beta_total;
    double l_star; /* Час життя миттєвих нейтронів (секунди) */
} ReactorParams;

typedef struct {
    double n;
    double C[NUM_GROUPS];
} State;

/* Обчислення похідних рівнянь точкової кінетики */
void compute_derivatives(const State *s, double rho, const ReactorParams *p, State *d) {
    double sum_lambda_C = 0.0;
    for (int i = 0; i < NUM_GROUPS; i++) {
        sum_lambda_C += p->lambda[i] * s->C[i];
    }
    
    /* dn/dt = ((rho - beta) / l*) * n + sum(lambda_i * C_i) */
    d->n = ((rho - p->beta_total) / p->l_star) * s->n + sum_lambda_C;
    
    /* dC_i/dt = (beta_i / l*) * n - lambda_i * C_i */
    for (int i = 0; i < NUM_GROUPS; i++) {
        d->C[i] = (p->beta[i] / p->l_star) * s->n - p->lambda[i] * s->C[i];
    }
}

/* Один крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
void rk4_step(State *s, double rho, const ReactorParams *p, double dt) {
    State k1, k2, k3, k4, temp;
    
    /* k1 */
    compute_derivatives(s, rho, p, &k1);
    
    /* k2 */
    temp.n = s->n + 0.5 * dt * k1.n;
    for (int i = 0; i < NUM_GROUPS; i++) {
        temp.C[i] = s->C[i] + 0.5 * dt * k1.C[i];
    }
    compute_derivatives(&temp, rho, p, &k2);
    
    /* k3 */
    temp.n = s->n + 0.5 * dt * k2.n;
    for (int i = 0; i < NUM_GROUPS; i++) {
        temp.C[i] = s->C[i] + 0.5 * dt * k2.C[i];
    }
    compute_derivatives(&temp, rho, p, &k3);
    
    /* k4 */
    temp.n = s->n + dt * k3.n;
    for (int i = 0; i < NUM_GROUPS; i++) {
        temp.C[i] = s->C[i] + dt * k3.C[i];
    }
    compute_derivatives(&temp, rho, p, &k4);
    
    /* Оновлення стану */
    s->n += (dt / 6.0) * (k1.n + 2.0 * k2.n + 2.0 * k3.n + k4.n);
    for (int i = 0; i < NUM_GROUPS; i++) {
        s->C[i] += (dt / 6.0) * (k1.C[i] + 2.0 * k2.C[i] + 2.0 * k3.C[i] + k4.C[i]);
    }
}

int main(void) {
    ReactorParams p = {
        .beta = {0.000215, 0.001424, 0.001274, 0.002568, 0.000748, 0.000273},
        .lambda = {0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01},
        .beta_total = 0.0065,
        .l_star = 1e-4
    };

    State s;
    s.n = 1.0; /* Початкова відносна потужність = 1.0 */
    
    /* У стаціонарному стані (rho = 0): dC_i/dt = 0 => C_i = (beta_i / (l* * lambda_i)) * n */
    for (int i = 0; i < NUM_GROUPS; i++) {
        s.C[i] = (p.beta[i] / (p.l_star * p.lambda[i])) * s.n;
    }

    double t = 0.0;
    double dt = 0.001; /* Крок інтегрування (секунди) */
    double t_max = 5.0;
    
    /* Введення позитивної реактивності rho = 0.002 (менше за beta = 0.0065) */
    double rho = 0.002;

    printf("Час [с]\tПотужність n(t)\tПеріод T [с]\n");
    printf("----------------------------------------\n");

    double prev_n = s.n;
    while (t <= t_max) {
        if ((int)(t / dt) % 500 == 0) {
            double dn_dt = (s.n - prev_n) / dt;
            double period = (dn_dt > 1e-9) ? (s.n / dn_dt) : 999.9;
            printf("%.2f\t%.4f\t\t%.2f\n", t, s.n, period);
        }
        prev_n = s.n;
        rk4_step(&s, rho, &p, dt);
        t += dt;
    }

    return 0;
}
