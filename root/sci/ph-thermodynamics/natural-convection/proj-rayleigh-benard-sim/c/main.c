#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 64
#define NY 32
#define MAX_ITER 1000
#define SOR_RELAX 1.75

typedef struct {
    double dx, dy, dt;
    double Ra, Pr;
    double T_bot, T_top;
    double theta[NY][NX];
    double omega[NY][NX];
    double psi[NY][NX];
    double u[NY][NX];
    double v[NY][NX];
} Simulation2D;

void init_simulation(Simulation2D *sim, double Ra, double Pr) {
    sim->dx = 2.0 / (NX - 1);
    sim->dy = 1.0 / (NY - 1);
    sim->dt = 0.0001;
    sim->Ra = Ra;
    sim->Pr = Pr;
    sim->T_bot = 1.0;
    sim->T_top = 0.0;

    for (int y = 0; y < NY; y++) {
        for (int x = 0; x < NX; x++) {
            double ly = y * sim->dy;
            double lx = x * sim->dx;
            /* Лінійне поле температури з малими збуреннями для ініціації нестійкості */
            sim->theta[y][x] = (1.0 - ly) + 0.05 * sin(M_PI * lx) * sin(M_PI * ly);
            sim->omega[y][x] = 0.0;
            sim->psi[y][x] = 0.0;
            sim->u[y][x] = 0.0;
            sim->v[y][x] = 0.0;
        }
    }
}

void solve_poisson_psi(Simulation2D *sim) {
    double dx2 = sim->dx * sim->dx;
    double dy2 = sim->dy * sim->dy;
    double factor = 0.5 * dx2 * dy2 / (dx2 + dy2);

    for (int iter = 0; iter < 100; iter++) {
        double max_err = 0.0;
        for (int y = 1; y < NY - 1; y++) {
            for (int x = 1; x < NX - 1; x++) {
                double psi_new = factor * ((sim->psi[y][x+1] + sim->psi[y][x-1]) / dx2 +
                                          (sim->psi[y+1][x] + sim->psi[y-1][x]) / dy2 +
                                          sim->omega[y][x]);
                double diff = psi_new - sim->psi[y][x];
                sim->psi[y][x] += SOR_RELAX * diff;
                if (fabs(diff) > max_err) max_err = fabs(diff);
            }
        }
        if (max_err < 1e-5) break;
    }
}

void step_simulation(Simulation2D *sim) {
    /* 1. Обчислення швидкостей з функції току */
    for (int y = 1; y < NY - 1; y++) {
        for (int x = 1; x < NX - 1; x++) {
            sim->u[y][x] = (sim->psi[y+1][x] - sim->psi[y-1][x]) / (2.0 * sim->dy);
            sim->v[y][x] = -(sim->psi[y][x+1] - sim->psi[y][x-1]) / (2.0 * sim->dx);
        }
    }

    /* 2. Оновлення поля температури та завихреності */
    static double dtheta[NY][NX];
    static double domega[NY][NX];

    double dx = sim->dx;
    double dy = sim->dy;

    for (int y = 1; y < NY - 1; y++) {
        for (int x = 1; x < NX - 1; x++) {
            /* Конвективні члени (центральні різниці) */
            double dth_dx = (sim->theta[y][x+1] - sim->theta[y][x-1]) / (2.0 * dx);
            double dth_dy = (sim->theta[y+1][x] - sim->theta[y-1][x]) / (2.0 * dy);
            double dom_dx = (sim->omega[y][x+1] - sim->omega[y][x-1]) / (2.0 * dx);
            double dom_dy = (sim->omega[y+1][x] - sim->omega[y-1][x]) / (2.0 * dy);

            /* Дифузійні члени (лапласіани) */
            double lap_th = (sim->theta[y][x+1] - 2.0*sim->theta[y][x] + sim->theta[y][x-1]) / (dx*dx) +
                            (sim->theta[y+1][x] - 2.0*sim->theta[y][x] + sim->theta[y-1][x]) / (dy*dy);
            double lap_om = (sim->omega[y][x+1] - 2.0*sim->omega[y][x] + sim->omega[y][x-1]) / (dx*dx) +
                            (sim->omega[y+1][x] - 2.0*sim->omega[y][x] + sim->omega[y-1][x]) / (dy*dy);

            /* Права частина для температури */
            dtheta[y][x] = -(sim->u[y][x] * dth_dx + sim->v[y][x] * dth_dy) + lap_th;

            /* Права частина для завихреності (включаючи джерело плавучості Ra * Pr * dtheta/dx) */
            domega[y][x] = -(sim->u[y][x] * dom_dx + sim->v[y][x] * dom_dy) +
                           sim->Pr * lap_om + sim->Ra * sim->Pr * dth_dx;
        }
    }

    /* Інтегрування за часом Ейлера */
    for (int y = 1; y < NY - 1; y++) {
        for (int x = 1; x < NX - 1; x++) {
            sim->theta[y][x] += sim->dt * dtheta[y][x];
            sim->omega[y][x] += sim->dt * domega[y][x];
        }
    }

    /* Граничні умови для завихреності на стінках (формула Тома) */
    for (int x = 0; x < NX; x++) {
        sim->omega[0][x] = -2.0 * sim->psi[1][x] / (dy * dy);
        sim->omega[NY-1][x] = -2.0 * sim->psi[NY-2][x] / (dy * dy);
    }

    /* 3. Розв'язання рівняння Пуассона для psi */
    solve_poisson_psi(sim);
}

int main(void) {
    Simulation2D sim;
    init_simulation(&sim, 3000.0, 0.71); /* Ra = 3000 (надкритичне), Pr = 0.71 (повітря) */

    printf("Початок моделювання конвекції Рейле-Бенара (Ra = %.1f)...\n", sim.Ra);
    for (int step = 0; step < MAX_ITER; step++) {
        step_simulation(&sim);
        if (step % 200 == 0) {
            printf("Крок %4d: Температура у центрі = %.4f, Psi_max = %.5f\n",
                   step, sim.theta[NY/2][NX/2], sim.psi[NY/2][NX/2]);
        }
    }
    printf("Моделювання завершено успішно.\n");
    return 0;
}
