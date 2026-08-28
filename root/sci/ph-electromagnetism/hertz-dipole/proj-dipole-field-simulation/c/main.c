#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define C_SPEED 299792458.0
#define EPSILON_0 8.8541878128e-12
#define PI 3.14159265358979323846

typedef struct {
    double r;        /* відстань від диполя, м */
    double theta;    /* кут від осі диполя, рад */
    double E_r;      /* радіальне ел. поле, В/м */
    double E_theta;  /* меридіональне ел. поле, В/м */
    double H_phi;    /* азимутальне магн. поле, А/м */
    double S_r;      /* миттєвий потік Пойнтінга, Вт/м² */
} DipoleFieldPoint;

DipoleFieldPoint compute_dipole_field(double r, double theta, double t,
                                     double I0, double dl, double freq) {
    DipoleFieldPoint pt;
    pt.r = r;
    pt.theta = theta;

    double omega = 2.0 * PI * freq;
    double k = omega / C_SPEED;
    double ret_t = t - r / C_SPEED;
    double phase = omega * ret_t;

    double cos_p = cos(phase);
    double sin_p = sin(phase);

    double sin_th = sin(theta);
    double cos_th = cos(theta);

    double r2 = r * r;
    double r3 = r2 * r;
    double k2 = k * k;

    double E_coeff = (I0 * dl) / (4.0 * PI * EPSILON_0 * omega);
    double H_coeff = (I0 * dl) / (4.0 * PI);

    pt.E_r = 2.0 * E_coeff * cos_th * (cos_p / r3 - k * sin_p / r2);
    pt.E_theta = E_coeff * sin_th * (cos_p / r3 - k * sin_p / r2 - k2 * cos_p / r);
    pt.H_phi = H_coeff * sin_th * (sin_p / r2 + k * cos_p / r);
    pt.S_r = pt.E_theta * pt.H_phi;

    return pt;
}

int main(void) {
    double freq = 100e6; /* 100 МГц */
    double lambda = C_SPEED / freq;
    double dl = 0.01 * lambda;
    double I0 = 1.0; /* 1 Ампер */
    double t = 0.0;

    printf("Частота = %.1f МГц, Довжина хвилі = %.3f м, dl = %.4f м\n",
           freq / 1e6, lambda, dl);
    printf("%-10s %-10s %-12s %-12s %-12s %-12s\n",
           "r/lambda", "r (м)", "E_r (В/м)", "E_theta (В/м)", "H_phi (А/м)", "S_r (Вт/м²)");

    double r_ratios[] = {0.01, 0.1, 0.159, 0.5, 1.0, 5.0};
    size_t count = sizeof(r_ratios) / sizeof(r_ratios[0]);

    for (size_t i = 0; i < count; i++) {
        double r = r_ratios[i] * lambda;
        DipoleFieldPoint pt = compute_dipole_field(r, PI / 2.0, t, I0, dl, freq);
        printf("%-10.3f %-10.4f %-12.4e %-12.4e %-12.4e %-12.4e\n",
               r_ratios[i], pt.r, pt.E_r, pt.E_theta, pt.H_phi, pt.S_r);
    }

    return 0;
}
