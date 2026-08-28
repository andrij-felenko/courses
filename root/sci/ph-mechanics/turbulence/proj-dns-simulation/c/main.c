/* DNS 2D Turbulence Spectral Solver (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef double complex dcomplex;

typedef struct {
    int N;
    double L;
    double nu;
    double dt;
    double *omega;
    dcomplex *omega_hat;
    dcomplex *rhs_hat;
} dns_solver_2d;

dns_solver_2d* dns_create(int N, double nu, double dt) {
    dns_solver_2d *s = (dns_solver_2d*)malloc(sizeof(dns_solver_2d));
    if (!s) return NULL;
    s->N = N;
    s->L = 2.0 * M_PI;
    s->nu = nu;
    s->dt = dt;
    
    int size = N * N;
    s->omega = (double*)calloc(size, sizeof(double));
    s->omega_hat = (dcomplex*)calloc(size, sizeof(dcomplex));
    s->rhs_hat = (dcomplex*)calloc(size, sizeof(dcomplex));
    
    if (!s->omega || !s->omega_hat || !s->rhs_hat) {
        free(s->omega);
        free(s->omega_hat);
        free(s->rhs_hat);
        free(s);
        return NULL;
    }
    return s;
}

void dns_free(dns_solver_2d *s) {
    if (s) {
        free(s->omega);
        free(s->omega_hat);
        free(s->rhs_hat);
        free(s);
    }
}

/* Двовимірне перетворення Фур'є для демонстрації алгоритму без FFTW */
void dft_2d(const double *in, dcomplex *out, int N, int forward) {
    double sign = forward ? -1.0 : 1.0;
    double norm = forward ? 1.0 : (1.0 / (N * N));
    
    for (int ky = 0; ky < N; ++ky) {
        for (int kx = 0; kx < N; ++kx) {
            dcomplex sum = 0.0 + 0.0 * I;
            for (int y = 0; y < N; ++y) {
                for (int x = 0; x < N; ++x) {
                    double angle = sign * 2.0 * M_PI * (kx * x + ky * y) / N;
                    sum += in[y * N + x] * (cos(angle) + I * sin(angle));
                }
            }
            out[ky * N + kx] = sum * norm;
        }
    }
}

void dns_init_vortex(dns_solver_2d *s) {
    int N = s->N;
    for (int y = 0; y < N; ++y) {
        double py = y * s->L / N;
        for (int x = 0; x < N; ++x) {
            double px = x * s->L / N;
            /* Початкове вихрове поле: сума двох гармонік */
            s->omega[y * N + x] = sin(4.0 * px) * cos(4.0 * py) - cos(2.0 * px) * sin(2.0 * py);
        }
    }
    dft_2d(s->omega, s->omega_hat, N, 1);
}

void dns_step(dns_solver_2d *s) {
    int N = s->N;
    double k_max_trunc = (2.0 / 3.0) * (N / 2);
    
    /* 1. Обчислення завихреності та дедемпфування у спектральному просторі */
    for (int ky = 0; ky < N; ++ky) {
        int iky = (ky <= N / 2) ? ky : (ky - N);
        for (int kx = 0; kx < N; ++kx) {
            int ikx = (kx <= N / 2) ? kx : (kx - N);
            double k2 = ikx * ikx + iky * iky;
            int idx = ky * N + kx;
            
            /* Правило 2/3 для усунення аліасингу */
            if (sqrt(k2) > k_max_trunc) {
                s->omega_hat[idx] = 0.0 + 0.0 * I;
            } else {
                /* В'язке згасання через експоненційний множник */
                double decay = exp(-s->nu * k2 * s->dt);
                s->omega_hat[idx] *= decay;
            }
        }
    }
}

double dns_calc_energy(const dns_solver_2d *s) {
    int N = s->N;
    double energy = 0.0;
    for (int i = 0; i < N * N; ++i) {
        energy += s->omega[i] * s->omega[i];
    }
    return 0.5 * energy / (N * N);
}

int main(void) {
    const int N = 32;
    dns_solver_2d *solver = dns_create(N, 0.001, 0.01);
    if (!solver) {
        fprintf(stderr, "Помилка виділення пам'яті солвера\n");
        return 1;
    }
    
    dns_init_vortex(solver);
    printf("Розпочато DNS моделювання 2D турбулентності (N=%d)...\n", N);
    
    for (int step = 0; step <= 100; step += 20) {
        double en = dns_calc_energy(solver);
        printf("Крок %3d | Енстрофія потоку: %.6f\n", step, en);
        for (int sub = 0; sub < 20; ++sub) {
            dns_step(solver);
        }
    }
    
    dns_free(solver);
    return 0;
}
