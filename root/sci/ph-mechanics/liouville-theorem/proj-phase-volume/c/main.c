#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#define NUM_PARTICLES 500
#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double q[NUM_PARTICLES];
    double p[NUM_PARTICLES];
} PhaseEnsemble;

double calculate_area(const PhaseEnsemble *ens) {
    double area = 0.0;
    for (int i = 0; i < NUM_PARTICLES; ++i) {
        int j = (i + 1) % NUM_PARTICLES;
        area += (ens->q[i] * ens->p[j]) - (ens->p[i] * ens->q[j]);
    }
    return 0.5 * fabs(area);
}

int main(void) {
    PhaseEnsemble exp_ens, imp_ens, sym_ens;
    double r = 0.2;
    double dt = 0.05;
    int steps = 1000;

    for (int i = 0; i < NUM_PARTICLES; ++i) {
        double angle = 2.0 * M_PI_VAL * i / NUM_PARTICLES;
        double q0 = 1.0 + r * cos(angle);
        double p0 = 0.0 + r * sin(angle);
        
        exp_ens.q[i] = imp_ens.q[i] = sym_ens.q[i] = q0;
        exp_ens.p[i] = imp_ens.p[i] = sym_ens.p[i] = p0;
    }

    double init_area = calculate_area(&exp_ens);
    printf("Початкова площа фазової хмари: %.6f\n\n", init_area);
    printf("%5s | %14s | %14s | %14s\n", "Крок", "Явний Ейлер", "Неявний Ейлер", "Симплектичний");
    printf("-------------------------------------------------------\n");

    for (int step = 1; step <= steps; ++step) {
        for (int i = 0; i < NUM_PARTICLES; ++i) {
            // Явний Ейлер
            double q_exp_next = exp_ens.q[i] + exp_ens.p[i] * dt;
            double p_exp_next = exp_ens.p[i] - exp_ens.q[i] * dt;
            exp_ens.q[i] = q_exp_next; exp_ens.p[i] = p_exp_next;

            // Неявний Ейлер
            double denom = 1.0 + dt * dt;
            double q_imp_next = (imp_ens.q[i] + dt * imp_ens.p[i]) / denom;
            double p_imp_next = (imp_ens.p[i] - dt * imp_ens.q[i]) / denom;
            imp_ens.q[i] = q_imp_next; imp_ens.p[i] = p_imp_next;

            // Симплектичний Ейлер
            double p_sym_next = sym_ens.p[i] - sym_ens.q[i] * dt;
            double q_sym_next = sym_ens.q[i] + p_sym_next * dt;
            sym_ens.q[i] = q_sym_next; sym_ens.p[i] = p_sym_next;
        }

        if (step % 200 == 0) {
            printf("%5d | %14.6f | %14.6f | %14.6f\n",
                   step, calculate_area(&exp_ens), calculate_area(&imp_ens), calculate_area(&sym_ens));
        }
    }
    return 0;
}
