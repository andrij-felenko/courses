#include <stdio.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x_m;
    double diameter_m;
    double area_m2;
} HornPoint;

typedef struct {
    double freq_hz;
    double r_norm;
    double x_norm;
} ImpedancePoint;

void calculate_horn_geometry(double d0_m, double dL_m, double fc_hz, double c, 
                             HornPoint* profile, int num_pts, double* out_L, double* out_m) {
    double S0 = M_PI * d0_m * d0_m / 4.0;
    double SL = M_PI * dL_m * dL_m / 4.0;
    
    double m = (4.0 * M_PI * fc_hz) / c;
    double L = log(SL / S0) / m;
    
    *out_m = m;
    *out_L = L;
    
    for (int i = 0; i <= num_pts; ++i) {
        double x = (L * i) / num_pts;
        double Sx = S0 * exp(m * x);
        profile[i].x_m = x;
        profile[i].area_m2 = Sx;
        profile[i].diameter_m = 2.0 * sqrt(Sx / M_PI);
    }
}

void calculate_infinite_impedance(double fc_hz, ImpedancePoint* spec, int num_freqs) {
    for (int i = 0; i < num_freqs; ++i) {
        double f = (3.0 * fc_hz * (i + 1)) / num_freqs;
        spec[i].freq_hz = f;
        if (f >= fc_hz) {
            spec[i].r_norm = sqrt(1.0 - (fc_hz / f) * (fc_hz / f));
            spec[i].x_norm = fc_hz / f;
        } else {
            spec[i].r_norm = 0.0;
            spec[i].x_norm = f / fc_hz;
        }
    }
}

int main(void) {
    double d0 = 0.0254; // 1 дюйм
    double dL = 0.30;   // 30 см
    double fc = 400.0;  // 400 Гц
    double c = 343.0;
    
    HornPoint profile[101];
    ImpedancePoint spec[100];
    double L = 0.0, m = 0.0;
    
    calculate_horn_geometry(d0, dL, fc, c, profile, 100, &L, &m);
    calculate_infinite_impedance(fc, spec, 100);
    
    printf("Експоненційний рупор: L = %.3f м, m = %.3f m^-1\n", L, m);
    printf("Гирло на x = %.3f м: d = %.3f м\n", profile[100].x_m, profile[100].diameter_m);
    printf("Імпеданс на 2*fc (800 Гц): R = %.4f, X = %.4f\n", spec[66].r_norm, spec[66].x_norm);
    
    return 0;
}
