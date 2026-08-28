#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define E_CHARGE 1.602176634e-19
#define KB_CONST 1.380649e-23

typedef struct {
    double C1, C2, Cg, C_total;
    double R1, R2;
    double Temp, Ec;
} SETParams;

static double tunnel_rate(double delta_F, double R_tunnel, double Temp) {
    if (fabs(delta_F) < 1e-30) {
        return (KB_CONST * Temp) / (E_CHARGE * E_CHARGE * R_tunnel);
    }
    double arg = delta_F / (KB_CONST * Temp);
    if (arg > 100.0) return 0.0;
    if (arg < -100.0) return -delta_F / (E_CHARGE * E_CHARGE * R_tunnel);
    return delta_F / (E_CHARGE * E_CHARGE * R_tunnel * (1.0 - exp(-arg)));
}

double calculate_set_current(const SETParams *sp, double Vds, double Vg, int n_max) {
    int num_states = 2 * n_max + 1;
    double *P = (double*)malloc(sizeof(double) * num_states);
    double *g1_plus = (double*)malloc(sizeof(double) * num_states);
    double *g1_minus = (double*)malloc(sizeof(double) * num_states);
    double *g2_plus = (double*)malloc(sizeof(double) * num_states);
    double *g2_minus = (double*)malloc(sizeof(double) * num_states);

    double Vs = Vds / 2.0;
    double Vd = -Vds / 2.0;

    for (int i = 0; i < num_states; i++) {
        int n = i - n_max;
        double n_ind = (sp->Cg * Vg + sp->C1 * Vs + sp->C2 * Vd) / E_CHARGE;
        
        double dF1_p = sp->Ec * (1.0 + 2.0 * (n - n_ind)) - E_CHARGE * Vs;
        double dF1_m = sp->Ec * (1.0 - 2.0 * (n - n_ind)) + E_CHARGE * Vs;
        double dF2_p = sp->Ec * (1.0 + 2.0 * (n - n_ind)) - E_CHARGE * Vd;
        double dF2_m = sp->Ec * (1.0 - 2.0 * (n - n_ind)) + E_CHARGE * Vd;

        g1_plus[i]  = tunnel_rate(dF1_p, sp->R1, sp->Temp);
        g1_minus[i] = tunnel_rate(dF1_m, sp->R1, sp->Temp);
        g2_plus[i]  = tunnel_rate(dF2_p, sp->R2, sp->Temp);
        g2_minus[i] = tunnel_rate(dF2_m, sp->R2, sp->Temp);
        P[i] = 0.0;
    }

    P[n_max] = 1.0;
    for (int i = n_max; i < num_states - 1; i++) {
        double W_p = g1_plus[i] + g2_plus[i];
        double W_m = g1_minus[i + 1] + g2_minus[i + 1];
        if (W_m > 0.0) P[i + 1] = P[i] * (W_p / W_m);
    }
    for (int i = n_max; i > 0; i--) {
        double W_m = g1_minus[i] + g2_minus[i];
        double W_p = g1_plus[i - 1] + g2_plus[i - 1];
        if (W_p > 0.0) P[i - 1] = P[i] * (W_m / W_p);
    }

    double sum_P = 0.0;
    for (int i = 0; i < num_states; i++) sum_P += P[i];
    for (int i = 0; i < num_states; i++) P[i] /= sum_P;

    double I_ds = 0.0;
    for (int i = 0; i < num_states; i++) {
        I_ds += E_CHARGE * P[i] * (g1_plus[i] - g1_minus[i]);
    }

    free(P); free(g1_plus); free(g1_minus); free(g2_plus); free(g2_minus);
    return I_ds;
}
