#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define HC_EV_NM 1239.84

typedef struct {
    double r_mean_nm;
    double sigma_r_nm;
    double e_g0_ev;
} QDProps;

double brus_gap_c(double r_nm, double e_g0) {
    if (r_nm <= 0.2) return e_g0;
    double conf = 3.73 / (r_nm * r_nm);
    double coul = 0.276 / r_nm;
    return e_g0 + conf - coul;
}

void compute_pl_spectrum_c(const QDProps* qd, double* wavelengths, double* spectrum, int n_points) {
    double wl_min = 400.0;
    double wl_max = 750.0;
    double step = (wl_max - wl_min) / (n_points - 1);
    
    for (int i = 0; i < n_points; ++i) {
        double wl = wl_min + i * step;
        double energy_ev = HC_EV_NM / wl;
        double total_intensity = 0.0;
        
        for (int j = -30; j <= 30; ++j) {
            double r = qd->r_mean_nm + j * 0.01;
            if (r <= 0.3) continue;
            
            double e_g = brus_gap_c(r, qd->e_g0_ev);
            double prob = (1.0 / (qd->sigma_r_nm * sqrt(2.0 * PI))) * 
                          exp(-0.5 * pow((r - qd->r_mean_nm) / qd->sigma_r_nm, 2.0));
            
            double gamma = 0.03;
            double lorentzian = (gamma / (2.0 * PI)) / (pow(energy_ev - e_g, 2.0) + pow(gamma / 2.0, 2.0));
            total_intensity += prob * lorentzian;
        }
        wavelengths[i] = wl;
        spectrum[i] = total_intensity;
    }
}

int main(void) {
    QDProps qd = { .r_mean_nm = 3.5, .sigma_r_nm = 0.2, .e_g0_ev = 1.74 };
    const int n_pts = 5;
    double wl[5], intensity[5];
    
    compute_pl_spectrum_c(&qd, wl, intensity, n_pts);
    printf("Обчислення спектра колоїдної точки (C):\n");
    for (int i = 0; i < n_pts; ++i) {
        printf("λ = %.1f нм, Інтенсивність = %.4f\n", wl[i], intensity[i]);
    }
    return 0;
}
