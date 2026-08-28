#include <stdio.h>
#include <math.h>

#define HBAR_C 0.19732698  /* ҐеВ * фм */
#define M_Z 91.1876        /* ҐеВ */
#define ALPHA_S_MZ 0.1179
#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double energy_gev;
    double boson_mass_gev;
    double target_mass_gev;
    double coupling;
} InteractionParams;

double calculate_yukawa_cross_section_c(const InteractionParams* p, double angle_rad) {
    double k = sqrt(p->energy_gev * p->energy_gev);
    double q_transfer = 2.0 * k * sin(angle_rad / 2.0);
    double denominator = q_transfer * q_transfer + p->boson_mass_gev * p->boson_mass_gev;
    
    double amplitude_fm = (2.0 * p->target_mass_gev * p->coupling * HBAR_C) / denominator;
    double cross_section_fm2 = amplitude_fm * amplitude_fm;
    return cross_section_fm2 * 0.01; /* Перетворення у барни */
}

double running_coupling_qcd_c(double q_gev, int n_flavors) {
    if (q_gev <= 0.3) return 1.0;
    
    double beta_0 = 11.0 - (2.0 / 3.0) * n_flavors;
    double ln_ratio = log((q_gev / M_Z) * (q_gev / M_Z));
    double denom = 1.0 + (beta_0 * ALPHA_S_MZ / (4.0 * M_PI_VAL)) * ln_ratio;
    
    return ALPHA_S_MZ / (denom > 0.01 ? denom : 0.01);
}

int main(void) {
    InteractionParams params = {0.5, 0.1395, 0.938, 1.0};
    double test_angles[] = {10.0, 30.0, 60.0, 90.0, 120.0, 150.0};
    size_t num_angles = sizeof(test_angles) / sizeof(test_angles[0]);
    
    printf("=== C Реалізація розрахунку перерізів ===\n");
    for (size_t i = 0; i < num_angles; ++i) {
        double rad = test_angles[i] * M_PI_VAL / 180.0;
        double dsig = calculate_yukawa_cross_section_c(&params, rad);
        printf("Кут %3.0f deg: dsigma/dOmega = %.6e barn/sr\n", test_angles[i], dsig);
    }
    
    printf("\nЗалежність alpha_s від Q:\n");
    double q_scales[] = {1.0, 10.0, 91.2, 1000.0};
    for (size_t i = 0; i < 4; ++i) {
        printf("Q = %6.1f GeV: alpha_s = %.4f\n", q_scales[i], running_coupling_qcd_c(q_scales[i], 5));
    }
    return 0;
}
