/* Simulation of Polarization Diversity in Rayleigh Fading (C standard) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double rho;
    double gamma_imbalance_db;
    double outage_single;
    double outage_sc;
    double outage_mrc;
} sim_results_t;

/* Box-Muller transform for standard complex normal distribution CN(0,1) */
static void generate_complex_gaussian(double *real_part, double *imag_part) {
    double u1 = (double)rand() / ((double)RAND_MAX + 1.0);
    double u2 = (double)rand() / ((double)RAND_MAX + 1.0);
    if (u1 < 1e-12) u1 = 1e-12;
    
    double radius = sqrt(-2.0 * log(u1));
    *real_part = (radius * cos(2.0 * M_PI * u2)) / sqrt(2.0);
    *imag_part = (radius * sin(2.0 * M_PI * u2)) / sqrt(2.0);
}

static sim_results_t run_diversity_simulation(size_t samples, double rho, double imbalance_db, double mean_snr_db, double threshold_db) {
    sim_results_t res = {0};
    res.rho = rho;
    res.gamma_imbalance_db = imbalance_db;

    double snr_linear = pow(10.0, mean_snr_db / 10.0);
    double thresh_linear = pow(10.0, threshold_db / 10.0);
    double imbalance_linear = pow(10.0, -imbalance_db / 10.0);
    
    double rho_c = sqrt(rho);
    double factor_ortho = sqrt(1.0 - rho_c * rho_c);
    
    size_t count_single_out = 0;
    size_t count_sc_out = 0;
    size_t count_mrc_out = 0;
    
    for (size_t i = 0; i < samples; ++i) {
        double w1_r, w1_i;
        double w2_r, w2_i;
        generate_complex_gaussian(&w1_r, &w1_i);
        generate_complex_gaussian(&w2_r, &w2_i);
        
        /* Channel 1 */
        double h1_r = w1_r;
        double h1_i = w1_i;
        
        /* Channel 2 correlated with Channel 1 */
        double h2_r = (rho_c * w1_r + factor_ortho * w2_r) * sqrt(imbalance_linear);
        double h2_i = (rho_c * w1_i + factor_ortho * w2_i) * sqrt(imbalance_linear);
        
        double g1 = (h1_r * h1_r + h1_i * h1_i) * snr_linear;
        double g2 = (h2_r * h2_r + h2_i * h2_i) * snr_linear;
        
        double g_sc = (g1 > g2) ? g1 : g2;
        double g_mrc = g1 + g2;
        
        if (g1 < thresh_linear) count_single_out++;
        if (g_sc < thresh_linear) count_sc_out++;
        if (g_mrc < thresh_linear) count_mrc_out++;
    }
    
    res.outage_single = (double)count_single_out / (double)samples;
    res.outage_sc = (double)count_sc_out / (double)samples;
    res.outage_mrc = (double)count_mrc_out / (double)samples;
    return res;
}

int main(void) {
    srand(12345); /* Fixed seed for reproducible output */
    size_t num_samples = 2000000;
    double threshold_db = 0.0;
    double mean_snr_db = 15.0;
    
    printf("=== Polarization Diversity Channel Simulation (C standard) ===\n");
    printf("Samples: %zu, Mean SNR: %.1f dB, Threshold: %.1f dB\n\n", num_samples, mean_snr_db, threshold_db);
    printf("%-10s %-14s %-16s %-16s %-16s\n", "Corr (rho)", "Imbalance", "Outage Single", "Outage SC", "Outage MRC");
    printf("-------------------------------------------------------------------------\n");
    
    double rhos[] = {0.0, 0.3, 0.5, 0.7, 0.9};
    for (size_t i = 0; i < sizeof(rhos)/sizeof(rhos[0]); ++i) {
        sim_results_t r = run_diversity_simulation(num_samples, rhos[i], 0.0, mean_snr_db, threshold_db);
        printf("%-10.1f %-14.1f %-16.4f %-16.5f %-16.5f\n", r.rho, r.gamma_imbalance_db, r.outage_single, r.outage_sc, r.outage_mrc);
    }

    printf("\n--- Test with Power Imbalance (Gamma = 4.0 dB) ---\n");
    for (size_t i = 0; i < sizeof(rhos)/sizeof(rhos[0]); ++i) {
        sim_results_t r = run_diversity_simulation(num_samples, rhos[i], 4.0, mean_snr_db, threshold_db);
        printf("%-10.1f %-14.1f %-16.4f %-16.5f %-16.5f\n", r.rho, r.gamma_imbalance_db, r.outage_single, r.outage_sc, r.outage_mrc);
    }
    
    return 0;
}
