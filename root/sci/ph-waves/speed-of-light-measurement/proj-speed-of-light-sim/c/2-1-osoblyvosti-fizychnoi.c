#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double distance_m;          /* Базова відстань L між вершинами (м) */
    double nominal_freq_hz;     /* Номінальна частота обертання ν (Гц) */
    int num_facets;             /* Кількість граней призми (N = 8) */
} MichelsonSystem;

/* Моделювання кутового зміщення променя при відхиленні частоти від синхронної */
double calculate_beam_deflection(const MichelsonSystem *sys, double actual_freq_hz, double c_val) {
    double t_flight = 2.0 * sys->distance_m / c_val;
    double facet_angle = 2.0 * M_PI / sys->num_facets;
    double rot_angle = 2.0 * M_PI * actual_freq_hz * t_flight;
    double delta_theta = rot_angle - facet_angle;
    return 2.0 * delta_theta; /* Відбитий промінь відхиляється на подвійний кут */
}

int main(void) {
    MichelsonSystem sys = { 35373.7, 528.25, 8 };
    double c_true = 299792458.0;
    double sync_freq = c_true / (2.0 * sys.num_facets * sys.distance_m);

    printf("=== Параметричний аналіз установки Майкельсона ===\n");
    printf("Синхронна частота обертання: %.3f Гц\n", sync_freq);
    printf("Частота (Гц) | Зсув променя (мрад) | Оцінена швидкість c (км/с) | Похилка (м/с)\n");
    printf("-----------------------------------------------------------------------------\n");

    for (double df = -2.0; df <= 2.0; df += 0.5) {
        double current_freq = sync_freq + df;
        double defl_rad = calculate_beam_deflection(&sys, current_freq, c_true);
        double c_calc = 2.0 * sys.num_facets * current_freq * sys.distance_m;
        double error_m_s = fabs(c_calc - c_true);

        printf("%12.3f | %19.4f | %26.2f | %13.2f\n", 
               current_freq, defl_rad * 1000.0, c_calc / 1000.0, error_m_s);
    }

    return 0;
}
