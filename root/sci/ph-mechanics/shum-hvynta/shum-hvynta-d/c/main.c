#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Обчислення J_n(x) степеневим рядом для x < n */
static double bessel_j(int n, double x) {
    if (x == 0.0) return (n == 0) ? 1.0 : 0.0;
    double half_x = 0.5 * x;
    double term = 1.0;
    for (int i = 1; i <= n; ++i) term *= (half_x / (double)i);
    double sum = term, half_x_sq = half_x * half_x;
    for (int k = 1; k < 50; ++k) {
        term *= -half_x_sq / ((double)k * (double)(n + k));
        sum += term;
        if (fabs(term) < 1e-14 * fabs(sum)) break;
    }
    return sum;
}

/* Розрахунок RMS акустичного тиску m-ї гармоніки Гутіна */
double gutin_harmonic_pressure(int m, int B, double rpm, double thrust_N, 
                              double torque_Nm, double radius_m, 
                              double distance_m, double theta_deg) {
    const double c0 = 343.0; // швидкість звуку, м/с
    double n_rps = rpm / 60.0;
    double omega = 2.0 * M_PI * n_rps;
    double r_eff = 0.80 * radius_m;
    double m_eff = (omega * r_eff) / c0;
    
    double theta_rad = theta_deg * M_PI / 180.0;
    double sin_theta = sin(theta_rad);
    double cos_theta = cos(theta_rad);
    
    int order = m * B;
    double arg_bessel = (double)order * m_eff * sin_theta;
    double j_val = bessel_j(order, arg_bessel);
    
    double bracket = -thrust_N * cos_theta + (c0 * torque_Nm) / (omega * r_eff * r_eff);
    double factor = ((double)order * omega) / (2.0 * sqrt(2.0) * M_PI * c0 * distance_m);
    
    return fabs(factor * bracket * j_val);
}
