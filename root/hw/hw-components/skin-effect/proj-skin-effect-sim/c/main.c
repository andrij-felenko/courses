#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

/* Обчислення модифікованої функції Бесселя I_0(z) через ряд Тейлора */
double complex bessel_i0_complex(double complex z) {
    double complex sum = 1.0 + 0.0*I;
    double complex term = 1.0 + 0.0*I;
    double complex z_sq_4 = (z * z) / 4.0;
    
    for (int k = 1; k <= 60; k++) {
        term = term * z_sq_4 / (double)(k * k);
        sum += term;
        if (cabs(term) < 1e-12 * cabs(sum)) {
            break;
        }
    }
    return sum;
}

/* Обчислення модифікованої функції Бесселя I_1(z) через ряд Тейлора */
double complex bessel_i1_complex(double complex z) {
    double complex sum = z / 2.0;
    double complex term = z / 2.0;
    double complex z_sq_4 = (z * z) / 4.0;
    
    for (int k = 1; k <= 60; k++) {
        term = term * z_sq_4 / (double)(k * (k + 1));
        sum += term;
        if (cabs(term) < 1e-12 * cabs(sum)) {
            break;
        }
    }
    return sum;
}

/* Обчислення глибини скін-шару delta (м) */
double calculate_skin_depth(double freq_hz, double sigma, double mu_r) {
    double mu0 = 4.0 * PI * 1e-7;
    double omega = 2.0 * PI * freq_hz;
    return sqrt(2.0 / (omega * (mu0 * mu_r) * sigma));
}

/* Обчислення відношення R_AC / R_DC */
double calculate_rac_rdc_ratio(double radius, double skin_depth) {
    if (skin_depth <= 0.0) return 1.0;
    
    double x = radius / skin_depth;
    if (x < 0.1) {
        return 1.0 + (1.0 / 48.0) * pow(x, 4.0);
    } else if (x > 15.0) {
        return 0.5 * x + 0.25 + 0.094 / x;
    }
    
    double complex k = (1.0 + 1.0*I) / skin_depth;
    double complex ka = k * radius;
    
    double complex i0 = bessel_i0_complex(ka);
    double complex i1 = bessel_i1_complex(ka);
    
    double complex ratio_complex = (ka / 2.0) * (i0 / i1);
    return creal(ratio_complex);
}

/* 1D FDM solver у C99 з алгоритмом Томаса */
int solve_1d_fdm_skin_effect(double thickness, size_t nodes, double freq_hz, 
                             const double* sigma_profile, double mu_r, 
                             double complex* out_e_field) {
    if (!sigma_profile || !out_e_field || nodes < 3) return -1;

    double mu0 = 4.0 * PI * 1e-7;
    double omega = 2.0 * PI * freq_hz;
    double dx = thickness / (double)(nodes - 1);

    double complex* b = (double complex*)malloc(nodes * sizeof(double complex));
    double complex* c_prime = (double complex*)malloc(nodes * sizeof(double complex));
    double complex* d_prime = (double complex*)malloc(nodes * sizeof(double complex));

    if (!b || !c_prime || !d_prime) {
        free(b); free(c_prime); free(d_prime);
        return -2;
    }

    /* Граничні умови */
    b[0] = 1.0 + 0.0*I;
    d_prime[0] = 1.0 + 0.0*I;
    c_prime[0] = 1.0 / b[0];

    for (size_t i = 1; i < nodes - 1; i++) {
        double sig = sigma_profile[i];
        b[i] = -2.0 - I * (omega * (mu0 * mu_r) * sig * dx * dx);
        
        double complex denom = b[i] - 1.0 * c_prime[i - 1];
        c_prime[i] = 1.0 / denom;
        d_prime[i] = (- 1.0 * d_prime[i - 1]) / denom;
    }

    out_e_field[nodes - 1] = 1.0 + 0.0*I;
    for (size_t i = nodes - 2; i < nodes; i--) {
        out_e_field[i] = d_prime[i] - c_prime[i] * out_e_field[i + 1];
    }

    free(b);
    free(c_prime);
    free(d_prime);
    return 0;
}

int main(void) {
    double radius = 0.001;        /* Радіус жили: 1 мм */
    double sigma = 5.8e7;         /* Питома провідність міді: 5.8e7 См/м */
    double mu_r = 1.0;            /* Відносна магнітна проникність */
    
    double frequencies[] = {50.0, 1e3, 10e3, 100e3, 1e6, 10e6};
    size_t num_freqs = sizeof(frequencies) / sizeof(frequencies[0]);
    
    printf("Частота (Гц)   | Скін-шар (мкм) | R_AC / R_DC\n");
    printf("---------------------------------------------\n");
    
    for (size_t i = 0; i < num_freqs; i++) {
        double f = frequencies[i];
        double delta = calculate_skin_depth(f, sigma, mu_r);
        double ratio = calculate_rac_rdc_ratio(radius, delta);
        
        printf("%-14.1e | %-14.2f | %-10.4f\n", f, delta * 1e6, ratio);
    }
    
    return 0;
}
