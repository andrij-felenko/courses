/*
 * three_body.c — Чисельне інтегрування задачі трьох тіл мовою C
 * Сімплектичний інтегратор Йошиди 4-го порядку (Yoshida 4th order integrator)
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_BODIES 3
#define G_CONST 1.0
#define SOFTENING_SQ 1e-12

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double mass;
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
} Body;

/* Обчислення прискорень усіх тіл за законом всесвітнього тяжіння */
static void compute_accelerations(Body bodies[NUM_BODIES]) {
    for (int i = 0; i < NUM_BODIES; i++) {
        bodies[i].acc.x = 0.0;
        bodies[i].acc.y = 0.0;
        bodies[i].acc.z = 0.0;
    }

    for (int i = 0; i < NUM_BODIES; i++) {
        for (int j = i + 1; j < NUM_BODIES; j++) {
            double dx = bodies[j].pos.x - bodies[i].pos.x;
            double dy = bodies[j].pos.y - bodies[i].pos.y;
            double dz = bodies[j].pos.z - bodies[i].pos.z;

            double dist_sq = dx * dx + dy * dy + dz * dz + SOFTENING_SQ;
            double dist = sqrt(dist_sq);
            double inv_dist3 = 1.0 / (dist_sq * dist);

            double f_i = G_CONST * bodies[j].mass * inv_dist3;
            double f_j = G_CONST * bodies[i].mass * inv_dist3;

            bodies[i].acc.x += dx * f_i;
            bodies[i].acc.y += dy * f_i;
            bodies[i].acc.z += dz * f_i;

            bodies[j].acc.x -= dx * f_j;
            bodies[j].acc.y -= dy * f_j;
            bodies[j].acc.z -= dz * f_j;
        }
    }
}

/* Обчислення повної механічної енергії E = K + U */
static double compute_total_energy(const Body bodies[NUM_BODIES]) {
    double kinetic = 0.0;
    double potential = 0.0;

    for (int i = 0; i < NUM_BODIES; i++) {
        double v_sq = bodies[i].vel.x * bodies[i].vel.x +
                      bodies[i].vel.y * bodies[i].vel.y +
                      bodies[i].vel.z * bodies[i].vel.z;
        kinetic += 0.5 * bodies[i].mass * v_sq;

        for (int j = i + 1; j < NUM_BODIES; j++) {
            double dx = bodies[j].pos.x - bodies[i].pos.x;
            double dy = bodies[j].pos.y - bodies[i].pos.y;
            double dz = bodies[j].pos.z - bodies[i].pos.z;
            double dist = sqrt(dx * dx + dy * dy + dz * dz + SOFTENING_SQ);
            potential -= (G_CONST * bodies[i].mass * bodies[j].mass) / dist;
        }
    }
    return kinetic + potential;
}

/* Один крок сімплектичного інтегратора Йошиди 4-го порядку */
static void step_yoshida4(Body bodies[NUM_BODIES], double dt) {
    /* Коефіцієнти Йошиди */
    static const double w0 = -1.7024143839193153;
    static const double w1 =  1.3512071919596578;
    
    static const double c[4] = {
        0.5 * 1.3512071919596578,
        0.5 * (1.3512071919596578 - 1.7024143839193153),
        0.5 * (1.3512071919596578 - 1.7024143839193153),
        0.5 * 1.3512071919596578
    };
    static const double d[3] = {
        1.3512071919596578,
        -1.7024143839193153,
        1.3512071919596578
    };

    for (int step = 0; step < 4; step++) {
        /* Оновлення координат */
        for (int i = 0; i < NUM_BODIES; i++) {
            bodies[i].pos.x += c[step] * bodies[i].vel.x * dt;
            bodies[i].pos.y += c[step] * bodies[i].vel.y * dt;
            bodies[i].pos.z += c[step] * bodies[i].vel.z * dt;
        }

        if (step < 3) {
            compute_accelerations(bodies);
            /* Оновлення швидкостей */
            for (int i = 0; i < NUM_BODIES; i++) {
                bodies[i].vel.x += d[step] * bodies[i].acc.x * dt;
                bodies[i].vel.y += d[step] * bodies[i].acc.y * dt;
                bodies[i].vel.z += d[step] * bodies[i].acc.z * dt;
            }
        }
    }
}

int main(void) {
    /* Початкові умови для класичної орбіти-вісімки (Figure-Eight choreography) */
    Body bodies[NUM_BODIES] = {
        {1.0, {-0.97000436,  0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {0}},
        {1.0, { 0.97000436, -0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {0}},
        {1.0, { 0.0,         0.0,        0.0}, {-0.93241062, -0.86473146, 0.0}, {0}}
    };

    double dt = 0.001;
    int steps = 10000;
    double initial_energy = compute_total_energy(bodies);

    printf("=== Симуляція задачі трьох тіл (C / Yoshida 4) ===\n");
    printf("Початкова енергія E0 = %.10f\n", initial_energy);

    for (int k = 1; k <= steps; k++) {
        step_yoshida4(bodies, dt);

        if (k % 2000 == 0) {
            double current_energy = compute_total_energy(bodies);
            double rel_err = fabs((current_energy - initial_energy) / initial_energy);
            printf("Крок %5d | E = %.10f | Відносна похибка E: %.2e\n",
                   k, current_energy, rel_err);
        }
    }

    return 0;
}
