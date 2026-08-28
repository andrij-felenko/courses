#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double i_ac;
    double omega;
    double beta_c;
    double h;
} RcsjParams;

void rcsj_derivs(double tau, double phi, double v, double i_dc, const RcsjParams* p, double* dphi, double* dv) {
    double gamma = 1.0 / sqrt(p->beta_c);
    *dphi = v;
    *dv = i_dc + p->i_ac * sin(p->omega * tau) - sin(phi) - gamma * v;
}

void rk4_step(double* tau, double* phi, double* v, double i_dc, const RcsjParams* p) {
    double h = p->h;
    double k1_phi, k1_v, k2_phi, k2_v, k3_phi, k3_v, k4_phi, k4_v;
    
    rcsj_derivs(*tau, *phi, *v, i_dc, p, &k1_phi, &k1_v);
    rcsj_derivs(*tau + 0.5 * h, *phi + 0.5 * h * k1_phi, *v + 0.5 * h * k1_v, i_dc, p, &k2_phi, &k2_v);
    rcsj_derivs(*tau + 0.5 * h, *phi + 0.5 * h * k2_phi, *v + 0.5 * h * k2_v, i_dc, p, &k3_phi, &k3_v);
    rcsj_derivs(*tau + h, *phi + h * k3_phi, *v + h * k3_v, i_dc, p, &k4_phi, &k4_v);
    
    *phi += (h / 6.0) * (k1_phi + 2.0 * k2_phi + 2.0 * k3_phi + k4_phi);
    *v += (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
    *tau += h;
}

double solve_single_point(double i_dc, const RcsjParams* p) {
    double period = 2.0 * M_PI / p->omega;
    int steps_per_period = (int)(period / p->h);
    int transient_steps = steps_per_period * 200;
    int eval_steps = steps_per_period * 500;
    
    double tau = 0.0, phi = 0.0, v = 0.0;
    for (int k = 0; k < transient_steps; ++k) {
        rk4_step(&tau, &phi, &v, i_dc, p);
    }
    
    double v_sum = 0.0;
    for (int k = 0; k < eval_steps; ++k) {
        rk4_step(&tau, &phi, &v, i_dc, p);
        v_sum += v;
    }
    return v_sum / eval_steps;
}

int main(void) {
    RcsjParams params = { .i_ac = 0.5, .omega = 0.6, .beta_c = 25.0, .h = 0.02 };
    printf("i_dc\t<v>\t<v>/omega\n");
    for (double i_dc = 0.0; i_dc <= 2.5; i_dc += 0.05) {
        double v_avg = solve_single_point(i_dc, &params);
        printf("%.2f\t%.4f\t%.4f\n", i_dc, v_avg, v_avg / params.omega);
    }
    return 0;
}
