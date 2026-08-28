/* 
 * blackbody_sim.c — Чисельне моделювання спектра Планка мовою C.
 * Компіляція: gcc -O2 -std=c99 blackbody_sim.c -lm -o blackbody_sim
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Fundamental physical constants (CODATA 2018) */
#define CONST_H  6.62607015e-34  /* Planck constant, J*s */
#define CONST_C  2.99792458e8    /* Speed of light, m/s */
#define CONST_KB 1.380649e-23    /* Boltzmann constant, J/K */
#define CONST_SIGMA 5.670374419e-8 /* Stefan-Boltzmann constant, W/(m^2*K^4) */

/* Spectral radiance R(lambda, T) in W/(m^2 * m) */
double planck_radiation_lambda(double lambda_m, double temp_k) {
    if (lambda_m <= 0.0 || temp_k <= 0.0) {
        return 0.0;
    }
    
    /* Argument of exponential: hc / (lambda * k * T) */
    double exponent_arg = (CONST_H * CONST_C) / (lambda_m * CONST_KB * temp_k);
    
    /* Protection against floating point overflow */
    if (exponent_arg > 700.0) {
        return 0.0;
    }
    
    double denominator = exp(exponent_arg) - 1.0;
    if (denominator <= 0.0) {
        return 0.0;
    }
    
    double numerator = 2.0 * M_PI * CONST_H * CONST_C * CONST_C;
    double lambda5 = lambda_m * lambda_m * lambda_m * lambda_m * lambda_m;
    
    return numerator / (lambda5 * denominator);
}

/* Numerical integration of R(lambda, T) over [lambda_a, lambda_b] using Simpson's 1/3 rule */
double integrate_planck_simpson(double temp_k, double lambda_a, double lambda_b, int num_steps) {
    if (num_steps % 2 != 0) {
        num_steps++; /* Simpson's rule requires an even number of intervals */
    }
    
    double h = (lambda_b - lambda_a) / num_steps;
    double sum = planck_radiation_lambda(lambda_a, temp_k) + planck_radiation_lambda(lambda_b, temp_k);
    
    for (int i = 1; i < num_steps; i++) {
        double lambda = lambda_a + i * h;
        double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * planck_radiation_lambda(lambda, temp_k);
    }
    
    return (h / 3.0) * sum;
}

/* Find peak wavelength (Wien's law) using Newton-Raphson method */
double find_wien_peak_lambda(double temp_k) {
    /* Solving 5*(1 - exp(-x)) = x for x */
    double x = 5.0;
    for (int iter = 0; iter < 20; iter++) {
        double f = 5.0 * (1.0 - exp(-x)) - x;
        double f_prime = 5.0 * exp(-x) - 1.0;
        double next_x = x - f / f_prime;
        if (fabs(next_x - x) < 1e-12) {
            x = next_x;
            break;
        }
        x = next_x;
    }
    return (CONST_H * CONST_C) / (CONST_KB * temp_k * x);
}

int main(void) {
    double temp_sun = 5778.0; /* Effective temperature of the Sun, K */
    
    printf("=== МОДЕЛЮВАННЯ ВИПРОМІНЮВАННЯ ЧОРНОГО ТІЛА (Сонце T = %.0f K) ===\n\n", temp_sun);
    
    /* 1. Peak wavelength */
    double lambda_peak = find_wien_peak_lambda(temp_sun);
    printf("1. Максимум випромінювання (Закон Віна):\n");
    printf("   lambda_max = %.2f нм (зелена частина видимого спектра)\n\n", lambda_peak * 1e9);
    
    /* 2. Spectral power density at key wavelengths */
    printf("2. Спектральна випромінювальна здатність R(lambda):\n");
    double test_lambdas_nm[] = {200.0, 380.0, 500.0, 750.0, 1500.0, 3000.0};
    int num_samples = sizeof(test_lambdas_nm) / sizeof(test_lambdas_nm[0]);
    
    for (int i = 0; i < num_samples; i++) {
        double lam_m = test_lambdas_nm[i] * 1e-9;
        double r_val = planck_radiation_lambda(lam_m, temp_sun);
        printf("   lambda = %6.1f нм: R = %12.4e Вт/(м^2 * м)\n", test_lambdas_nm[i], r_val);
    }
    
    /* 3. Total flux integration vs Stefan-Boltzmann theory */
    double lambda_start = 1e-9;    /* 1 nm */
    double lambda_end   = 50e-6;   /* 50 um */
    double flux_simpson = integrate_planck_simpson(temp_sun, lambda_start, lambda_end, 10000);
    double flux_theory  = CONST_SIGMA * pow(temp_sun, 4.0);
    
    printf("\n3. Інтегральний потік випромінювання:\n");
    printf("   Чисельне інтегрування (1 нм - 50 мкм): %.4e Вт/м^2\n", flux_simpson);
    printf("   Теоретичне значення (Закон Стефана-Больцмана): %.4e Вт/м^2\n", flux_theory);
    printf("   Відносна похибка: %.4f%%\n", fabs(flux_simpson - flux_theory) / flux_theory * 100.0);
    
    return 0;
}
