#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI_CONST 3.14159265358979323846

typedef struct {
    double wp;      /* плазмова частота (еВ) */
    double gamma;   /* частота розсіяння (еВ) */
    double eps_inf; /* диелектрична проникність остова */
    double eps_d;   /* проникність середовища */
    double n_prism; /* показник заломлення призми */
} drude_params_t;

typedef struct {
    double omega_eV;
    double eps_real;
    double eps_imag;
    double n_ref;
    double k_ext;
    double reflectivity;
    double k_spp_real;
    double kretschmann_deg;
} plasmon_point_t;

static double complex drude_epsilon(double omega, const drude_params_t* p) {
    if (omega <= 0.0) return p->eps_inf + 0.0 * I;
    double complex denom = (omega * omega) + I * (p->gamma * omega);
    return p->eps_inf - (p->wp * p->wp) / denom;
}

static double drude_reflectivity(double complex eps) {
    double complex n_comp = csqrt(eps);
    double complex r_amp = (1.0 - n_comp) / (1.0 + n_comp);
    return cabs(r_amp) * cabs(r_amp);
}

static double complex drude_k_spp(double omega, double complex eps_m, double eps_d) {
    double complex eps_d_comp = eps_d + 0.0 * I;
    double complex ratio = (eps_m * eps_d_comp) / (eps_m + eps_d_comp);
    return omega * csqrt(ratio);
}

static double kretschmann_angle(double complex k_spp, double omega, double n_prism) {
    double sin_th = creal(k_spp) / (omega * n_prism);
    if (sin_th > 1.0 || sin_th < -1.0) return 0.0;
    return asin(sin_th) * (180.0 / PI_CONST);
}

int main(void) {
    drude_params_t silver = {
        .wp = 9.01,
        .gamma = 0.05,
        .eps_inf = 3.7,
        .eps_d = 1.0,
        .n_prism = 1.517
    };

    const int steps = 10;
    double start_eV = 1.0;
    double end_eV = 3.5;
    double step_size = (end_eV - start_eV) / (steps - 1);

    printf("===========================================================================================\n");
    printf("  w (eV)  |   Re(eps)   |   Im(eps)   |    n    |    k    | Reflectivity R | Angle (deg)\n");
    printf("===========================================================================================\n");

    for (int i = 0; i < steps; ++i) {
        double w = start_eV + i * step_size;
        double complex eps = drude_epsilon(w, &silver);
        double complex n_comp = csqrt(eps);
        double R = drude_reflectivity(eps);
        double complex k_spp = drude_k_spp(w, eps, silver.eps_d);
        double angle = kretschmann_angle(k_spp, w, silver.n_prism);

        printf("  %6.3f  |  %9.3f  |  %9.3f  |  %6.3f | %6.3f | %12.3f  | %9.3f\n",
               w, creal(eps), cimag(eps), creal(n_comp), cimag(n_comp), R, angle);
    }
    printf("===========================================================================================\n");
    return 0;
}
