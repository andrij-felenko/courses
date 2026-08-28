#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи моделі Годжкіна-Гакслі */
static const double C_M = 1.0;
static const double G_NA = 120.0;
static const double G_K = 36.0;
static const double G_L = 0.3;
static const double E_NA = 50.0;
static const double E_K = -77.0;
static const double E_L = -54.387;

/* Обхід сингулярності вида x / (1 - exp(-x/10)) при x -> 0 */
static double alpha_m(double V) {
    double x = V + 40.0;
    if (fabs(x) < 1e-6) return 1.0;
    return 0.1 * x / (1.0 - exp(-x / 10.0));
}

static double beta_m(double V) {
    return 4.0 * exp(-(V + 65.0) / 18.0);
}

static double alpha_h(double V) {
    return 0.07 * exp(-(V + 65.0) / 20.0);
}

static double beta_h(double V) {
    return 1.0 / (1.0 + exp(-(V + 35.0) / 10.0));
}

static double alpha_n(double V) {
    double x = V + 55.0;
    if (fabs(x) < 1e-6) return 0.1;
    return 0.01 * x / (1.0 - exp(-x / 10.0));
}

static double beta_n(double V) {
    return 0.125 * exp(-(V + 65.0) / 80.0);
}

typedef struct {
    double V;
    double m;
    double h;
    double n;
} HHState;

static HHState hh_init(double V_rest) {
    HHState s;
    s.V = V_rest;
    double a_m = alpha_m(V_rest);
    double b_m = beta_m(V_rest);
    double a_h = alpha_h(V_rest);
    double b_h = beta_h(V_rest);
    double a_n = alpha_n(V_rest);
    double b_n = beta_n(V_rest);

    s.m = a_m / (a_m + b_m);
    s.h = a_h / (a_h + b_h);
    s.n = a_n / (a_n + b_n);
    return s;
}

/* Інтегрування ворітних змінних методом Раша-Ларсена для максимальної стійкості */
static void hh_step_rush_larsen(HHState *s, double I_ext, double dt) {
    double V = s->V;
    double m = s->m;
    double h = s->h;
    double n = s->n;

    /* Обчислення струмів за поточними значеннями воріт */
    double I_Na = G_NA * (m * m * m) * h * (V - E_NA);
    double I_K  = G_K * (n * n * n * n) * (V - E_K);
    double I_L  = G_L * (V - E_L);

    /* Оновлення напруги за методом Ейлера */
    double dVdt = (I_ext - I_Na - I_K - I_L) / C_M;
    s->V += dVdt * dt;

    /* Аналітичне інтегрування воріт Раша-Ларсена */
    double a_m = alpha_m(V), b_m = beta_m(V);
    double m_inf = a_m / (a_m + b_m);
    double tau_m = 1.0 / (a_m + b_m);
    s->m = m_inf + (m - m_inf) * exp(-dt / tau_m);

    double a_h = alpha_h(V), b_h = beta_h(V);
    double h_inf = a_h / (a_h + b_h);
    double tau_h = 1.0 / (a_h + b_h);
    s->h = h_inf + (h - h_inf) * exp(-dt / tau_h);

    double a_n = alpha_n(V), b_n = beta_n(V);
    double n_inf = a_n / (a_n + b_n);
    double tau_n = 1.0 / (a_n + b_n);
    s->n = n_inf + (n - n_inf) * exp(-dt / tau_n);
}

int main(void) {
    double t_max = 50.0; /* 50 мс */
    double dt = 0.01;   /* 0.01 мс */
    HHState state = hh_init(-65.0);

    printf("# t(ms)\tV(mV)\tm\th\tn\n");

    for (double t = 0.0; t <= t_max; t += dt) {
        /* Стимулюючий струм 10 мкА/см² між t = 10 мс та t = 12 мс */
        double I_ext = (t >= 10.0 && t <= 12.0) ? 10.0 : 0.0;

        if ((int)(t / dt) % 100 == 0) {
            printf("%.2f\t%.2f\t%.3f\t%.3f\t%.3f\n", t, state.V, state.m, state.h, state.n);
        }

        hh_step_rush_larsen(&state, I_ext, dt);
    }

    return 0;
}
