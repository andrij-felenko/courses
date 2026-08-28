#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define K_B_EV 8.617333e-5
#define Q_ELEC 1.602176e-19

typedef struct {
    double et_minus_ei_ev; /* E_t - E_i (еВ) */
    double tau_n0_s;       /* τ_n0 (с) */
    double tau_p0_s;       /* τ_p0 (с) */
} srh_trap_params_t;

typedef struct {
    double r_srh;          /* см⁻³·с⁻¹ */
    double tau_eff_s;      /* с */
    bool is_generation;
} srh_result_t;

int srh_compute(const srh_trap_params_t* params, double n, double p, 
                double temp_k, double n_i, srh_result_t* out_result) {
    if (!params || !out_result || temp_k <= 0.0 || n_i <= 0.0) {
        return -1;
    }
    
    double vt = K_B_EV * temp_k;
    double exp_factor = exp(params->et_minus_ei_ev / vt);
    double n_1 = n_i * exp_factor;
    double p_1 = n_i / exp_factor;
    
    double ni_sq = n_i * n_i;
    double numerator = n * p - ni_sq;
    double denominator = params->tau_p0_s * (n + n_1) + params->tau_n0_s * (p + p_1);
    
    if (denominator <= 0.0) {
        return -2;
    }
    
    out_result->r_srh = numerator / denominator;
    out_result->is_generation = (numerator < 0.0);
    
    double delta_n = n - (ni_sq / (p > 1.0 ? p : 1.0));
    if (delta_n < 1e-12) delta_n = 1e-12;
    
    out_result->tau_eff_s = (out_result->r_srh > 0.0) ? (delta_n / out_result->r_srh) : 0.0;
    
    return 0;
}

int main(void) {
    srh_trap_params_t trap = { .et_minus_ei_ev = 0.02, .tau_n0_s = 1e-6, .tau_p0_s = 1e-6 };
    double p0 = 1e16;
    double n_i = 1.5e10;
    
    printf("--- (C) SRH recombination rate vs injection level ---\n");
    for (double log_dn = 10.0; log_dn <= 17.0; log_dn += 1.0) {
        double dn = pow(10.0, log_dn);
        double n = (n_i * n_i / p0) + dn;
        double p = p0 + dn;
        
        srh_result_t res;
        if (srh_compute(&trap, n, p, 300.0, n_i, &res) == 0) {
            printf("Δn = %.1e cm-3 | R = %.2e cm-3 s-1 | tau = %.3f us\n",
                   dn, res.r_srh, res.tau_eff_s * 1e6);
        }
    }
    return 0;
}
