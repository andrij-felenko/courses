#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фізичні константи */
#define EPSILON_0 8.854e-12

typedef struct {
    double tau;         /* час релаксації в секундах */
    double chi_stat;    /* статична сприйнятливість */
    double eps_inf;     /* високочастотна проникність */
} DielectricModel;

/* Обчислення крок за кроком методом Ейлера-Рафсона */
int simulate_debye_relaxation(
    const DielectricModel *model,
    const double *E_field,
    double *P_out,
    size_t num_steps,
    double dt
) {
    if (!model || !E_field || !P_out || num_steps == 0 || dt <= 0.0) {
        return -1;
    }

    double P_current = 0.0;
    for (size_t i = 0; i < num_steps; ++i) {
        double P_eq = EPSILON_0 * model->chi_stat * E_field[i];
        double dP_dt = (P_eq - P_current) / model->tau;
        P_current += dP_dt * dt;
        P_out[i] = P_current;
    }

    return 0;
}

/* Аналітичне обчислення спектра Дебая */
void compute_debye_spectrum(
    const DielectricModel *model,
    double freq_start_hz,
    double freq_end_hz,
    size_t num_points,
    double *out_eps_real,
    double *out_eps_imag
) {
    double log_start = log10(freq_start_hz);
    double log_end = log10(freq_end_hz);
    double log_step = (log_end - log_start) / (double)(num_points - 1);

    double eps_s = model->eps_inf + model->chi_stat;

    for (size_t i = 0; i < num_points; ++i) {
        double freq = pow(10.0, log_start + i * log_step);
        double omega = 2.0 * M_PI * freq;
        double omega_tau = omega * model->tau;

        out_eps_real[i] = model->eps_inf + (eps_s - model->eps_inf) / (1.0 + omega_tau * omega_tau);
        out_eps_imag[i] = (eps_s - model->eps_inf) * omega_tau / (1.0 + omega_tau * omega_tau);
    }
}

int main(void) {
    DielectricModel water_model = {
        .tau = 8.2e-12,     /* 8.2 пікосекунди для води при 25°C */
        .chi_stat = 77.5,
        .eps_inf = 4.9
    };

    const size_t num_steps = 1000;
    const double dt = 1.0e-13; /* 0.1 пікосекунди */
    
    double *E_field = (double *)malloc(num_steps * sizeof(double));
    double *P_out = (double *)malloc(num_steps * sizeof(double));

    if (!E_field || !P_out) {
        free(E_field);
        free(P_out);
        return 1;
    }

    /* Подаємо стрибок напруженості поля E = 10^6 В/м */
    for (size_t i = 0; i < num_steps; ++i) {
        E_field[i] = 1.0e6;
    }

    if (simulate_debye_relaxation(&water_model, E_field, P_out, num_steps, dt) == 0) {
        printf("--- Симуляція стрибка поляризації (вода) ---\n");
        printf("Крок 0 (t=0.0 ps):  P = %.4e Кл/м^2\n", P_out[0]);
        printf("Крок 100 (t=10 ps): P = %.4e Кл/м^2\n", P_out[100]);
        printf("Крок 999 (t=100ps): P = %.4e Кл/м^2\n", P_out[999]);
    }

    free(E_field);
    free(P_out);
    return 0;
}
