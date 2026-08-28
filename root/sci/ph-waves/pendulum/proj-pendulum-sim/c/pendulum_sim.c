/* pendulum_sim.c - Чисельне моделювання маятника мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double length;      /* Довжина нитки L (м) */
    double gravity;     /* Прискорення вільного падіння g (м/с²) */
    double dt;          /* Крок інтегрування за часом (с) */
} pendulum_params_t;

typedef struct {
    double theta;       /* Кут відхилення (рад) */
    double omega;       /* Кутова швидкість (рад/с) */
    double time;        /* Поточний час (с) */
} pendulum_state_t;

/* Обчислення похідних: dtheta/dt = omega, domega/dt = -(g/L)*sin(theta) */
static void pendulum_derivatives(const pendulum_params_t *p, double theta, double omega,
                                 double *d_theta, double *d_omega) {
    *d_theta = omega;
    *d_omega = -(p->gravity / p->length) * sin(theta);
}

/* Один крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
void pendulum_step_rk4(const pendulum_params_t *p, pendulum_state_t *s) {
    double k1_th, k1_om;
    double k2_th, k2_om;
    double k3_th, k3_om;
    double k4_th, k4_om;

    pendulum_derivatives(p, s->theta, s->omega, &k1_th, &k1_om);

    pendulum_derivatives(p, s->theta + 0.5 * p->dt * k1_th,
                         s->omega + 0.5 * p->dt * k1_om,
                         &k2_th, &k2_om);

    pendulum_derivatives(p, s->theta + 0.5 * p->dt * k2_th,
                         s->omega + 0.5 * p->dt * k2_om,
                         &k3_th, &k3_om);

    pendulum_derivatives(p, s->theta + p->dt * k3_th,
                         s->omega + p->dt * k3_om,
                         &k4_th, &k4_om);

    s->theta += (p->dt / 6.0) * (k1_th + 2.0 * k2_th + 2.0 * k3_th + k4_th);
    s->omega += (p->dt / 6.0) * (k1_om + 2.0 * k2_om + 2.0 * k3_om + k4_om);
    s->time += p->dt;
}

/* Обчислення повної питомої енергії системи */
double pendulum_energy(const pendulum_params_t *p, const pendulum_state_t *s) {
    double e_kin = 0.5 * p->length * p->length * s->omega * s->omega;
    double e_pot = p->gravity * p->length * (1.0 - cos(s->theta));
    return e_kin + e_pot;
}

/* Теоретичний період через 4 члени еліптичного ряду */
double pendulum_period_elliptic(double length, double gravity, double theta0_deg) {
    double theta0 = theta0_deg * (PI / 180.0);
    double t0 = 2.0 * PI * sqrt(length / gravity);
    double k = sin(theta0 / 2.0);
    double k2 = k * k;
    double k4 = k2 * k2;
    double k6 = k4 * k2;
    
    double series = 1.0 + (1.0/4.0)*k2 + (9.0/64.0)*k4 + (225.0/2304.0)*k6;
    return t0 * series;
}

int main(void) {
    pendulum_params_t params = { .length = 1.0, .gravity = 9.80665, .dt = 0.001 };
    double angles[] = { 5.0, 30.0, 60.0, 90.0, 120.0, 150.0 };
    size_t num_angles = sizeof(angles) / sizeof(angles[0]);

    printf("=== МОДЕЛЮВАННЯ НЕЛАКТИВНОГО МАЯТНИКА (RK4) ===\n");
    printf("Кут (deg) | Т_симуляції (с) | Т_еліптичний (с) | Похибка (%%)\n");
    printf("-----------------------------------------------------------\n");

    for (size_t i = 0; i < num_angles; i++) {
        double deg0 = angles[i];
        pendulum_state_t state = { .theta = deg0 * (PI / 180.0), .omega = 0.0, .time = 0.0 };
        
        double prev_theta = state.theta;
        double t_first_peak = -1.0;
        double t_second_peak = -1.0;

        while (state.time < 20.0 && t_second_peak < 0.0) {
            double old_th = state.theta;
            pendulum_step_rk4(&params, &state);

            if (old_th > 0 && state.theta <= old_th && prev_theta < old_th) {
                if (t_first_peak < 0) {
                    t_first_peak = state.time - params.dt;
                } else if (t_second_peak < 0) {
                    t_second_peak = state.time - params.dt;
                }
            }
            prev_theta = old_th;
        }

        double t_sim = (t_second_peak > 0) ? (t_second_peak - t_first_peak) : 0.0;
        double t_ell = pendulum_period_elliptic(params.length, params.gravity, deg0);
        double err = fabs(t_sim - t_ell) / t_ell * 100.0;

        printf("  %5.1f°  |    %8.5f     |    %8.5f     |   %6.4f%%\n",
               deg0, t_sim, t_ell, err);
    }

    return 0;
}
