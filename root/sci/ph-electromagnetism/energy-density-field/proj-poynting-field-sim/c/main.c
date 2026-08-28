#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні сталі */
#define EPS0 8.8541878128e-12
#define MU0  1.2566370614e-6
#define C0   299792458.0

/* Параметри сітки */
#define NZ 200
#define TIMESTEPS 300

typedef struct {
    double e[NZ];
    double h[NZ];
    double w_e[NZ];
    double w_m[NZ];
    double s[NZ];
} fdtd_domain_t;

void fdtd_init(fdtd_domain_t *domain) {
    for (int i = 0; i < NZ; i++) {
        domain->e[i] = 0.0;
        domain->h[i] = 0.0;
        domain->w_e[i] = 0.0;
        domain->w_m[i] = 0.0;
        domain->s[i] = 0.0;
    }
}

void fdtd_step(fdtd_domain_t *dom, double dz, double dt, int t_step) {
    double ch = dt / (MU0 * dz);
    double ce = dt / (EPS0 * dz);

    /* 1. Оновлення магнітного поля H */
    for (int i = 0; i < NZ - 1; i++) {
        dom->h[i] -= ch * (dom->e[i + 1] - dom->e[i]);
    }

    /* 2. Оновлення електричного поля E */
    for (int i = 1; i < NZ; i++) {
        dom->e[i] -= ce * (dom->h[i] - dom->h[i - 1]);
    }

    /* 3. Джерело гаусового імпульсу у центрі */
    double t0 = 40.0;
    double spread = 12.0;
    double pulse = exp(-0.5 * pow((t_step - t0) / spread, 2.0));
    dom->e[NZ / 2] += pulse;

    /* 4. Розрахунок енергетичних характеристик */
    for (int i = 1; i < NZ - 1; i++) {
        double h_avg = 0.5 * (dom->h[i] + dom->h[i - 1]);
        dom->w_e[i] = 0.5 * EPS0 * dom->e[i] * dom->e[i];
        dom->w_m[i] = 0.5 * MU0 * h_avg * h_avg;
        dom->s[i]   = dom->e[i] * h_avg;
    }
}

int main(void) {
    fdtd_domain_t dom;
    fdtd_init(&dom);

    double dz = 1e-3; /* 1 мм */
    double dt = dz / (2.0 * C0); /* Courant number = 0.5 */

    printf("Крок | Вузол 100 E | Густина w_e (Дж/м³) | Потік S (Вт/м²)\n");
    printf("-----------------------------------------------------------\n");

    for (int t = 0; t < TIMESTEPS; t++) {
        fdtd_step(&dom, dz, dt, t);
        if (t % 50 == 0) {
            int mid = NZ / 2;
            printf("%4d | %11.4e | %19.4e | %16.4e\n",
                   t, dom.e[mid], dom.w_e[mid], dom.s[mid]);
        }
    }

    return 0;
}
