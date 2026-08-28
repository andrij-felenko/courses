#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double y0;
    double z_surf;
    double z_focus;
    double ds_prime;
    double u_prime_deg;
} RayResult;

int trace_ray(double R, double n1, double n2, double y0, RayResult *out) {
    if (fabs(y0) >= fabs(R)) return 0;

    double z_paraxial = (n2 * R) / (n2 - n1);
    double z_surf = R - sqrt(R * R - y0 * y0);
    double sin_alpha = y0 / R;
    double sin_theta2 = (n1 / n2) * sin_alpha;
    
    if (fabs(sin_theta2) > 1.0) return 0; // Повне внутрішнє відбиття
    
    double alpha = asin(sin_alpha);
    double theta2 = asin(sin_theta2);
    double u_prime = alpha - theta2;

    out->y0 = y0;
    out->z_surf = z_surf;
    
    if (fabs(u_prime) < 1e-12) {
        out->z_focus = z_paraxial;
    } else {
        out->z_focus = z_surf + y0 / tan(u_prime);
    }
    
    out->ds_prime = out->z_focus - z_paraxial;
    out->u_prime_deg = u_prime * (180.0 / M_PI);
    return 1;
}

int main(void) {
    double R = 100.0, n1 = 1.0, n2 = 1.5;
    double z_p = (n2 * R) / (n2 - n1);
    printf("Параксіальний фокус z_p = %.4f мм\n\n", z_p);
    printf("%8s | %11s | %12s | %10s | %10s\n", 
           "y0 (мм)", "z_surf (мм)", "z_focus (мм)", "ds_prime", "U' (град)");
    printf("----------------------------------------------------------------\n");

    double heights[] = {5.0, 10.0, 20.0, 30.0, 40.0, 50.0};
    for (size_t i = 0; i < sizeof(heights)/sizeof(heights[0]); ++i) {
        RayResult res;
        if (trace_ray(R, n1, n2, heights[i], &res)) {
            printf("%8.1f | %11.4f | %12.4f | %10.4f | %10.4f\n",
                   res.y0, res.z_surf, res.z_focus, res.ds_prime, res.u_prime_deg);
        }
    }
    return 0;
}
