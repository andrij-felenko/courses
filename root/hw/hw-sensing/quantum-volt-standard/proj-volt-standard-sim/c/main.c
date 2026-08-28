#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double beta_c;     /* Параметр Стюарта-Маккамбера (0.1 для overdamped) */
    double omega_rf;   /* Нормована частота СВЧ (f_rf / f_J0) */
    double i_rf;       /* Нормована амплітуда СВЧ струму */
    double dt;         /* Крок інтегрування по безрозмірному часу */
    int trans_steps;   /* Кількість кроків для затухання переходного процесу */
    int avg_steps;     /* Кількість кроків для усереднення напруги */
} JosephsonConfig;

typedef struct {
    double phi;
    double v;
} State;

static State derivatives(State s, double t, double i_bias, const JosephsonConfig *cfg) {
    State d;
    d.phi = s.v;
    double i_total = i_bias + cfg->i_rf * cos(cfg->omega_rf * t);
    d.v = (i_total - sin(s.phi) - s.v) / cfg->beta_c;
    return d;
}

static State rk4_step(State s, double t, double i_bias, const JosephsonConfig *cfg) {
    double dt = cfg->dt;
    
    State k1 = derivatives(s, t, i_bias, cfg);
    
    State s2 = { s.phi + 0.5 * dt * k1.phi, s.v + 0.5 * dt * k1.v };
    State k2 = derivatives(s2, t + 0.5 * dt, i_bias, cfg);
    
    State s3 = { s.phi + 0.5 * dt * k2.phi, s.v + 0.5 * dt * k2.v };
    State k3 = derivatives(s3, t + 0.5 * dt, i_bias, cfg);
    
    State s4 = { s.phi + dt * k3.phi, s.v + dt * k3.v };
    State k4 = derivatives(s4, t + dt, i_bias, cfg);
    
    State res;
    res.phi = s.phi + (dt / 6.0) * (k1.phi + 2.0 * k2.phi + 2.0 * k3.phi + k4.phi);
    res.v   = s.v   + (dt / 6.0) * (k1.v   + 2.0 * k2.v   + 2.0 * k3.v   + k4.v);
    return res;
}

int main(void) {
    JosephsonConfig cfg = {
        .beta_c = 0.2,
        .omega_rf = 1.0,
        .i_rf = 1.2,
        .dt = 0.05,
        .trans_steps = 4000,
        .avg_steps = 10000
    };

    printf("Simulating Shapiro steps for overdamped Josephson Junction (C)\n");
    printf("i_bias\t\t<v>\t\tStep Index (n = <v>/w_rf)\n");

    State current_state = { 0.0, 0.0 };

    for (double i_bias = 0.0; i_bias <= 3.0; i_bias += 0.05) {
        double t = 0.0;
        
        /* Пропуск перехідного процесу */
        for (int step = 0; step < cfg.trans_steps; ++step) {
            current_state = rk4_step(current_state, t, i_bias, &cfg);
            t += cfg.dt;
        }

        /* Усереднення напруги */
        double v_sum = 0.0;
        for (int step = 0; step < cfg.avg_steps; ++step) {
            current_state = rk4_step(current_state, t, i_bias, &cfg);
            v_sum += current_state.v;
            t += cfg.dt;
        }

        double v_avg = v_sum / cfg.avg_steps;
        double step_index = v_avg / cfg.omega_rf;

        printf("%.3f\t\t%.5f\t\t%.2f\n", i_bias, v_avg, step_index);
    }

    return 0;
}
