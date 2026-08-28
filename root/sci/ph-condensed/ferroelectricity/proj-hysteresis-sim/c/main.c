#include <stdio.h>
#include <math.h>

#define PI 3.14159265358979323846

/* Структура параметрів сегнетоелектрика */
typedef struct {
    double alpha;    /* α0*(T - T0) < 0 */
    double beta;     /* β > 0 */
    double gamma;    /* релаксаційна стала γ */
    double e_amp;    /* амплітуда зовнішнього поля E0 */
    double freq;     /* частота поля f */
    double e_bias;   /* внутрішнє поле зсуву */
} FerroParams;

/* Похідна dP/dt = f(t, P) */
static double deriv_p(double t, double p, const FerroParams *params) {
    double e_field = params->e_amp * sin(2.0 * PI * params->freq * t) + params->e_bias;
    double df_dp = params->alpha * p + params->beta * p * p * p - e_field;
    return -df_dp / params->gamma;
}

/* Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
static double step_rk4(double t, double p, double dt, const FerroParams *params) {
    double k1 = deriv_p(t, p, params);
    double k2 = deriv_p(t + 0.5 * dt, p + 0.5 * dt * k1, params);
    double k3 = deriv_p(t + 0.5 * dt, p + 0.5 * dt * k2, params);
    double k4 = deriv_p(t + dt, p + dt * k3, params);
    return p + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
}

int main(void) {
    FerroParams params = {
        .alpha = -1.0,
        .beta = 1.0,
        .gamma = 0.1,
        .e_amp = 1.5,
        .freq = 1.0,
        .e_bias = 0.0
    };

    double t = 0.0;
    double p = 0.1; /* початкова поляризація */
    double dt = 0.0005;
    int total_steps = 4000;
    double energy_loss = 0.0;
    double prev_e = 0.0;
    double prev_p = 0.1;

    printf("Time,E_field,Polarization\n");
    for (int i = 0; i < total_steps; i++) {
        double e_field = params.e_amp * sin(2.0 * PI * params.freq * t) + params.e_bias;
        
        /* Розрахунок втрат на останньому усталеному циклі за методом трапецій */
        if (i >= 2000) {
            printf("%.4f,%.4f,%.4f\n", t, e_field, p);
            double dp = p - prev_p;
            double avg_e = 0.5 * (e_field + prev_e);
            energy_loss += avg_e * dp;
        }
        
        prev_e = e_field;
        prev_p = p;
        p = step_rk4(t, p, dt, &params);
        t += dt;
    }

    fprintf(stderr, "Обчислена площа петлі (втрати W): %.4f у.о.\n", energy_loss);
    return 0;
}
