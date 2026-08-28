#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define MU_0 1.2566370614359173e-6

typedef enum {
    ANISOTROPY_UNIAXIAL,
    ANISOTROPY_CUBIC
} AnisotropyType;

typedef struct {
    double Ms;              /* Saturation magnetization (A/m) */
    double K1;              /* First anisotropy constant (J/m^3) */
    double K2;              /* Second anisotropy constant (J/m^3) */
    AnisotropyType type;
} MagneticMaterial;

typedef struct {
    double H_amp;           /* Field amplitude (A/m) */
    double psi_deg;         /* Field angle in degrees relative to z-axis */
} AppliedField;

/* Calculate anisotropy energy density E_A */
double calc_anisotropy_energy(const MagneticMaterial* mat, double theta, double phi) {
    if (mat->type == ANISOTROPY_UNIAXIAL) {
        double sin_t = sin(theta);
        double sin2_t = sin_t * sin_t;
        double sin4_t = sin2_t * sin4_t;
        return mat->K1 * sin2_t + mat->K2 * sin4_t;
    } else {
        /* Cubic anisotropy */
        double a1 = sin(theta) * cos(phi);
        double a2 = sin(theta) * sin(phi);
        double a3 = cos(theta);
        double a1_2 = a1 * a1, a2_2 = a2 * a2, a3_2 = a3 * a3;
        return mat->K1 * (a1_2 * a2_2 + a2_2 * a3_2 + a3_2 * a1_2) + mat->K2 * (a1_2 * a2_2 * a3_2);
    }
}

/* Calculate total free energy density E = E_A + E_Zeeman */
double calc_total_energy_uniaxial(const MagneticMaterial* mat, double H, double psi, double theta) {
    double E_A = mat->K1 * sin(theta) * sin(theta) + mat->K2 * pow(sin(theta), 4);
    double E_Z = -MU_0 * mat->Ms * H * cos(psi - theta);
    return E_A + E_Z;
}

/* Golden section search for local minimum of 1D energy function */
double find_energy_minimum_1d(const MagneticMaterial* mat, double H, double psi, double theta_start) {
    double a = theta_start - PI / 4.0;
    double b = theta_start + PI / 4.0;
    const double phi_gold = (1.0 + sqrt(5.0)) / 2.0;
    const double resphi = 2.0 - phi_gold;
    
    double x1 = a + resphi * (b - a);
    double x2 = b - resphi * (b - a);
    double f1 = calc_total_energy_uniaxial(mat, H, psi, x1);
    double f2 = calc_total_energy_uniaxial(mat, H, psi, x2);
    
    for (int iter = 0; iter < 60; ++iter) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = a + resphi * (b - a);
            f1 = calc_total_energy_uniaxial(mat, H, psi, x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = b - resphi * (b - a);
            f2 = calc_total_energy_uniaxial(mat, H, psi, x2);
        }
        if (fabs(b - a) < 1e-7) break;
    }
    return (a + b) / 2.0;
}

/* Simulate M(H) magnetization curve */
void simulate_magnetization_curve(const MagneticMaterial* mat, double psi_deg, double H_max, int steps) {
    double psi = psi_deg * PI / 180.0;
    double theta_curr = (cos(psi) >= 0) ? 0.0 : PI;
    double H_step = 2.0 * H_max / steps;

    printf("# H (A/m)\tM_parallel / M_s\tTheta (deg)\n");
    for (int i = 0; i <= steps; ++i) {
        double H = -H_max + i * H_step;
        theta_curr = find_energy_minimum_1d(mat, H, psi, theta_curr);
        double m_parallel = cos(psi - theta_curr);
        printf("%.2f\t%.6f\t%.2f\n", H, m_parallel, theta_curr * 180.0 / PI);
    }
}

int main(void) {
    /* Cobalt parameters: Ms = 1.4e6 A/m, K1 = 4.1e5 J/m^3, K2 = 1.0e5 J/m^3 */
    MagneticMaterial cobalt = {
        .Ms = 1.4e6,
        .K1 = 4.1e5,
        .K2 = 1.0e5,
        .type = ANISOTROPY_UNIAXIAL
    };

    printf("=== Симуляція намагнічування Co уздовж важкої осі (90 град) ===\n");
    simulate_magnetization_curve(&cobalt, 90.0, 1.2e6, 50);

    return 0;
}
