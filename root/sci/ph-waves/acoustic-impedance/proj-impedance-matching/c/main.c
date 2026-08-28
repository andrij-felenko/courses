#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SIZE 1000
#define TIME_STEPS 1400
#define PI 3.14159265358979323846

typedef struct {
    double p[GRID_SIZE];
    double v[GRID_SIZE];
    double rho[GRID_SIZE];
    double K[GRID_SIZE];
    double c[GRID_SIZE];
} AcousticDomain;

void init_domain(AcousticDomain *d, double z1, double z2, int use_matching_layer) {
    double c1 = 1500.0; // speed of sound in medium 1 (m/s)
    double rho1 = z1 / c1;
    double K1 = z1 * c1;

    double c2 = 1500.0; // speed of sound in medium 2 (m/s)
    double rho2 = z2 / c2;
    double K2 = z2 * c2;

    int interface_pos = 500;
    double freq = 1.0e6; // 1 MHz center frequency
    double lambda_m = c1 / freq;
    int layer_thickness = (int)((lambda_m / 4.0) / (0.0001)); // in grid cells (dx = 0.1 mm)

    if (layer_thickness < 1) layer_thickness = 1;

    double zm = sqrt(z1 * z2);
    double rhom = zm / c1;
    double Km = zm * c1;

    for (int i = 0; i < GRID_SIZE; i++) {
        d->p[i] = 0.0;
        d->v[i] = 0.0;

        if (i < interface_pos) {
            d->rho[i] = rho1;
            d->K[i] = K1;
            d->c[i] = c1;
        } else if (use_matching_layer && i < (interface_pos + layer_thickness)) {
            d->rho[i] = rhom;
            d->K[i] = Km;
            d->c[i] = c1;
        } else {
            d->rho[i] = rho2;
            d->K[i] = K2;
            d->c[i] = c2;
        }
    }
}

void step_fdtd(AcousticDomain *d, double dx, double dt, int t_step) {
    // Store old values at boundaries for Mur ABC
    double p0_old = d->p[0];
    double p1_old = d->p[1];
    double pN1_old = d->p[GRID_SIZE - 1];
    double pN2_old = d->p[GRID_SIZE - 2];

    // Update particle velocity v
    for (int i = 0; i < GRID_SIZE - 1; i++) {
        double rho_avg = 0.5 * (d->rho[i] + d->rho[i + 1]);
        d->v[i] -= (dt / (rho_avg * dx)) * (d->p[i + 1] - d->p[i]);
    }

    // Update acoustic pressure p
    for (int i = 1; i < GRID_SIZE - 1; i++) {
        d->p[i] -= (dt * d->K[i] / dx) * (d->v[i] - d->v[i - 1]);
    }

    // Mur 1st Order Absorbing Boundary Conditions (ABC)
    double c0 = d->c[0];
    double gamma0 = (c0 * dt - dx) / (c0 * dt + dx);
    d->p[0] = p1_old + gamma0 * (d->p[1] - p0_old);

    double cN = d->c[GRID_SIZE - 1];
    double gammaN = (cN * dt - dx) / (cN * dt + dx);
    d->p[GRID_SIZE - 1] = pN2_old + gammaN * (d->p[GRID_SIZE - 2] - pN1_old);

    // Source injection (Gaussian pulse at node 100)
    double t = t_step * dt;
    double t0 = 35.0 * dt;
    double spread = 10.0 * dt;
    d->p[100] += exp(-0.5 * ((t - t0) / spread) * ((t - t0) / spread));
}

int main(void) {
    double dx = 0.0001; // 0.1 mm spatial resolution
    double dt = 3.0e-8; // 30 ns time step (satisfies CFL condition)

    AcousticDomain direct_domain;
    AcousticDomain matched_domain;

    // Media impedances: Medium 1 = 1.5 MRayl, Medium 2 = 6.0 MRayl
    init_domain(&direct_domain, 1.5e6, 6.0e6, 0);
    init_domain(&matched_domain, 1.5e6, 6.0e6, 1);

    for (int t = 0; t < TIME_STEPS; t++) {
        step_fdtd(&direct_domain, dx, dt, t);
        step_fdtd(&matched_domain, dx, dt, t);
    }

    // Measure peak amplitude of reflected pulse at node 300
    double direct_ref = fabs(direct_domain.p[300]);
    double matched_ref = fabs(matched_domain.p[300]);

    printf("=== Результати FDTD моделювання імпедансного узгодження ===\n");
    printf("Амплітуда відбиття без узгодження (прямий контакт): %.4f\n", direct_ref);
    printf("Амплітуда відбиття з чвертьхвильовим шаром:        %.4f\n", matched_ref);
    printf("Приглушення відбитої хвилі:                         %.1f%%\n",
           (1.0 - matched_ref / direct_ref) * 100.0);

    return 0;
}
