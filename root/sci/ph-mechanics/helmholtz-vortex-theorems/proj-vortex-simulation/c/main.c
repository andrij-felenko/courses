#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
    double gamma;
} vortex_t;

typedef struct {
    int num_vortices;
    double core_eps_sq; /* ε² для регуляризації ядра */
    vortex_t *vortices;
} vortex_system_t;

/* Обчислення швидкостей усіх вихорів dr/dt = f(r) */
void compute_velocities(const vortex_system_t *sys, double *vx, double *vy) {
    int n = sys->num_vortices;
    double eps2 = sys->core_eps_sq;
    double inv_2pi = 1.0 / (2.0 * M_PI);

    for (int i = 0; i < n; i++) {
        double u_sum = 0.0;
        double v_sum = 0.0;
        double xi = sys->vortices[i].x;
        double yi = sys->vortices[i].y;

        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            double dx = xi - sys->vortices[j].x;
            double dy = yi - sys->vortices[j].y;
            double r2 = dx * dx + dy * dy + eps2;
            double factor = inv_2pi * sys->vortices[j].gamma / r2;

            u_sum += -dy * factor;
            v_sum +=  dx * factor;
        }
        vx[i] = u_sum;
        vy[i] = v_sum;
    }
}

/* Крок чисельного інтегрування методом Рунге — Кутти 4-го порядку (RK4) */
void rk4_step(vortex_system_t *sys, double dt) {
    int n = sys->num_vortices;
    double *vx1 = (double*)malloc(n * sizeof(double));
    double *vy1 = (double*)malloc(n * sizeof(double));
    double *vx2 = (double*)malloc(n * sizeof(double));
    double *vy2 = (double*)malloc(n * sizeof(double));
    double *vx3 = (double*)malloc(n * sizeof(double));
    double *vy3 = (double*)malloc(n * sizeof(double));
    double *vx4 = (double*)malloc(n * sizeof(double));
    double *vy4 = (double*)malloc(n * sizeof(double));

    vortex_system_t tmp;
    tmp.num_vortices = n;
    tmp.core_eps_sq = sys->core_eps_sq;
    tmp.vortices = (vortex_t*)malloc(n * sizeof(vortex_t));

    for (int i = 0; i < n; i++) tmp.vortices[i] = sys->vortices[i];

    /* K1 */
    compute_velocities(&tmp, vx1, vy1);

    /* K2 */
    for (int i = 0; i < n; i++) {
        tmp.vortices[i].x = sys->vortices[i].x + 0.5 * dt * vx1[i];
        tmp.vortices[i].y = sys->vortices[i].y + 0.5 * dt * vy1[i];
    }
    compute_velocities(&tmp, vx2, vy2);

    /* K3 */
    for (int i = 0; i < n; i++) {
        tmp.vortices[i].x = sys->vortices[i].x + 0.5 * dt * vx2[i];
        tmp.vortices[i].y = sys->vortices[i].y + 0.5 * dt * vy2[i];
    }
    compute_velocities(&tmp, vx3, vy3);

    /* K4 */
    for (int i = 0; i < n; i++) {
        tmp.vortices[i].x = sys->vortices[i].x + dt * vx3[i];
        tmp.vortices[i].y = sys->vortices[i].y + dt * vy3[i];
    }
    compute_velocities(&tmp, vx4, vy4);

    /* Оновлення координат за інтегральною формою RK4 */
    for (int i = 0; i < n; i++) {
        sys->vortices[i].x += (dt / 6.0) * (vx1[i] + 2.0 * vx2[i] + 2.0 * vx3[i] + vx4[i]);
        sys->vortices[i].y += (dt / 6.0) * (vy1[i] + 2.0 * vy2[i] + 2.0 * vy3[i] + vy4[i]);
    }

    free(vx1); free(vy1); free(vx2); free(vy2);
    free(vx3); free(vy3); free(vx4); free(vy4);
    free(tmp.vortices);
}

/* Обчислення момента імпульсу системи (інваріанта) */
double compute_angular_momentum(const vortex_system_t *sys) {
    double M = 0.0;
    for (int i = 0; i < sys->num_vortices; i++) {
        double r2 = sys->vortices[i].x * sys->vortices[i].x + sys->vortices[i].y * sys->vortices[i].y;
        M += sys->vortices[i].gamma * r2;
    }
    return M;
}

int main(void) {
    vortex_system_t sys;
    sys.num_vortices = 4;
    sys.core_eps_sq = 0.01 * 0.01;
    sys.vortices = (vortex_t*)malloc(4 * sizeof(vortex_t));

    /* Конфігурація двох коаксіальних вихорових пар */
    sys.vortices[0] = (vortex_t){.x = -1.0, .y =  0.5, .gamma =  1.0};
    sys.vortices[1] = (vortex_t){.x = -1.0, .y = -0.5, .gamma = -1.0};
    sys.vortices[2] = (vortex_t){.x =  0.0, .y =  1.0, .gamma =  1.0};
    sys.vortices[3] = (vortex_t){.x =  0.0, .y = -1.0, .gamma = -1.0};

    double dt = 0.01;
    int steps = 1000;
    double M0 = compute_angular_momentum(&sys);

    printf("=== Симуляція динаміки вихорів RK4 (C implementation) ===\n");
    printf("Початковий момент імпульсу M0: %.8f\n\n", M0);

    for (int step = 0; step <= steps; step++) {
        if (step % 200 == 0) {
            double M_curr = compute_angular_momentum(&sys);
            printf("Крок %4d | t = %5.2f | В1(%.3f, %.3f) | В3(%.3f, %.3f) | M = %.8f (Err: %.2e)\n",
                   step, step * dt,
                   sys.vortices[0].x, sys.vortices[0].y,
                   sys.vortices[2].x, sys.vortices[2].y,
                   M_curr, fabs(M_curr - M0));
        }
        rk4_step(&sys, dt);
    }

    free(sys.vortices);
    return 0;
}
