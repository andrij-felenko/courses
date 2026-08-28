/* C99: Обчислення коефіцієнта відбиття та КСХ */
#include <stdio.h>
#include <math.h>
#include <complex.h>

typedef struct {
    double complex gamma;
    double vswr;
    double return_loss_db;
} smith_point_t;

smith_point_t smith_analyze_impedance(double complex z_load, double z0) {
    smith_point_t result;
    double complex z_norm = z_load / z0;
    
    /* Γ = (z - 1) / (z + 1) */
    result.gamma = (z_norm - 1.0) / (z_norm + 1.0);
    double g_abs = cabs(result.gamma);
    
    if (g_abs >= 0.9999) {
        result.vswr = 999.0;
        result.return_loss_db = 0.0;
    } else {
        result.vswr = (1.0 + g_abs) / (1.0 - g_abs);
        result.return_loss_db = -20.0 * log10(g_abs);
    }
    
    return result;
}

void print_smith_summary(double complex z_load, double z0) {
    smith_point_t pt = smith_analyze_impedance(z_load, z0);
    printf("Z = %.1f + j%.1f Ом | Γ = %.3f ∠%.1f° | КСХ = %.2f:1 | RL = %.2f дБ\n",
           creal(z_load), cimag(z_load),
           cabs(pt.gamma), carg(pt.gamma) * 180.0 / M_PI,
           pt.vswr, pt.return_loss_db);
}
