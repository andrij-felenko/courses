/* thermal_expansion_sim.c - Симуляція теплового розширення 1D кристала (C11) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N_ATOMS 50
#define DT 0.002
#define TOTAL_STEPS 200000
#define THERMALIZATION_STEPS 50000

typedef struct {
    double x[N_ATOMS];
    double v[N_ATOMS];
    double f[N_ATOMS];
    double mass;
    double epsilon;
    double sigma;
    double gamma;
} Crystal;

/* Генератор нормального розподілу Бокса-Мюллера */
double rand_gaussian(double stddev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12;
    return stddev * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

void compute_forces(Crystal *c) {
    for (int i = 0; i < N_ATOMS; i++) c->f[i] = 0.0;
    
    /* Сили взаємодії між сусідніми атомами */
    for (int i = 0; i < N_ATOMS - 1; i++) {
        double r = c->x[i+1] - c->x[i];
        if (r < 0.1) r = 0.1;
        double sr = c->sigma / r;
        double sr6 = sr * sr * sr * sr * sr * sr;
        double sr12 = sr6 * sr6;
        /* F = -dU/dr = 24*eps/r * (2*(sigma/r)^12 - (sigma/r)^6) */
        double force = (24.0 * c->epsilon / r) * (2.0 * sr12 - sr6);
        c->f[i] -= force;
        c->f[i+1] += force;
    }
}

double simulate_temperature(double target_temp) {
    Crystal c;
    c.mass = 1.0;
    c.epsilon = 1.0;
    c.sigma = 1.0;
    c.gamma = 1.0;
    
    double r0 = pow(2.0, 1.0 / 6.0) * c.sigma;
    for (int i = 0; i < N_ATOMS; i++) {
        c.x[i] = i * r0;
        c.v[i] = 0.0;
    }
    
    double noise_std = sqrt(2.0 * c.gamma * c.mass * target_temp / DT);
    compute_forces(&c);
    
    double sum_length = 0.0;
    int count = 0;
    
    for (int step = 0; step < TOTAL_STEPS; step++) {
        /* Velocity Verlet 1-й крок */
        for (int i = 0; i < N_ATOMS; i++) {
            c.v[i] += 0.5 * DT * (c.f[i] - c.gamma * c.v[i] + rand_gaussian(noise_std)) / c.mass;
            c.x[i] += DT * c.v[i];
        }
        
        compute_forces(&c);
        
        /* Velocity Verlet 2-й крок */
        for (int i = 0; i < N_ATOMS; i++) {
            c.v[i] += 0.5 * DT * (c.f[i] - c.gamma * c.v[i] + rand_gaussian(noise_std)) / c.mass;
        }
        
        if (step >= THERMALIZATION_STEPS) {
            double current_length = c.x[N_ATOMS - 1] - c.x[0];
            sum_length += current_length;
            count++;
        }
    }
    
    return sum_length / count;
}

int main(void) {
    srand(12345);
    printf("Temperature,Average_Length,Delta_L_Percent\n");
    
    double temps[] = {0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30};
    int num_t = sizeof(temps) / sizeof(temps[0]);
    
    double L0 = (N_ATOMS - 1) * pow(2.0, 1.0 / 6.0);
    
    for (int i = 0; i < num_t; i++) {
        double avg_l = simulate_temperature(temps[i]);
        double delta_pct = ((avg_l - L0) / L0) * 100.0;
        printf("%.2f,%.5f,%.3f%%\n", temps[i], avg_l, delta_pct);
    }
    
    return 0;
}
