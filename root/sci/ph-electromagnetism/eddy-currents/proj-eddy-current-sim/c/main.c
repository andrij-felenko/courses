#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double sigma;       // Провідність (См/м)
    double mu_r;        // Магнітна проникність
    double thickness;   // Товщина (м)
    double frequency;   // Частота (Гц)
    double B_0;         // Індукція (Тл)
    size_t nodes;       // Кількість вузлів
} simulation_params_t;

int run_eddy_simulation(const simulation_params_t* params, double* out_power_loss) {
    if (!params || !out_power_loss || params->nodes < 3) {
        return -1;
    }

    const double mu_0 = 4.0 * PI * 1e-7;
    const double mu = params->mu_r * mu_0;
    const double omega = 2.0 * PI * params->frequency;
    const double dx = params->thickness / (double)(params->nodes - 1);
    const double D_m = 1.0 / (mu * params->sigma);

    const double dt = 0.45 * (dx * dx) / D_m;
    const double alpha = D_m * dt / (dx * dx);

    double* B = (double*)calloc(params->nodes, sizeof(double));
    double* B_next = (double*)calloc(params->nodes, sizeof(double));
    double* j_y = (double*)calloc(params->nodes, sizeof(double));

    if (!B || !B_next || !j_y) {
        free(B);
        free(B_next);
        free(j_y);
        return -2;
    }

    const double period = 1.0 / params->frequency;
    const double total_time = 5.0 * period;
    const size_t num_steps = (size_t)(total_time / dt);

    double t = 0.0;
    for (size_t step = 0; step < num_steps; ++step) {
        t += dt;
        const double B_ext = params->B_0 * sin(omega * t);

        for (size_t i = 1; i < params->nodes - 1; ++i) {
            B_next[i] = B[i] + alpha * (B[i + 1] - 2.0 * B[i] + B[i - 1]);
        }
        B_next[0] = B_ext;
        B_next[params->nodes - 1] = B_ext;

        for (size_t i = 0; i < params->nodes; ++i) {
            B[i] = B_next[i];
        }
    }

    // Обчислення струму
    for (size_t i = 1; i < params->nodes - 1; ++i) {
        j_y[i] = -(1.0 / mu) * (B[i + 1] - B[i - 1]) / (2.0 * dx);
    }
    j_y[0] = -(1.0 / mu) * (B[1] - B[0]) / dx;
    j_y[params->nodes - 1] = -(1.0 / mu) * (B[params->nodes - 1] - B[params->nodes - 2]) / dx;

    // Інтегрування потужності
    double integrated_power = 0.0;
    for (size_t i = 0; i < params->nodes; ++i) {
        double p_local = (j_y[i] * j_y[i]) / params->sigma;
        double weight = (i == 0 || i == params->nodes - 1) ? 0.5 : 1.0;
        integrated_power += p_local * weight * dx;
    }

    *out_power_loss = integrated_power / params->thickness;

    free(B);
    free(B_next);
    free(j_y);

    return 0;
}

int main(void) {
    simulation_params_t params = {
        .sigma = 5.8e7,
        .mu_r = 1.0,
        .thickness = 0.002,
        .frequency = 1000.0,
        .B_0 = 0.1,
        .nodes = 101
    };

    double power_loss = 0.0;
    if (run_eddy_simulation(&params, &power_loss) == 0) {
        printf("Об'ємні втрати P_e: %.2f кВт/м³\n", power_loss * 1e-3);
    } else {
        fprintf(stderr, "Помилка симуляції.\n");
    }

    return 0;
}
