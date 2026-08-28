#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define M_PI 3.14159265358979323846

typedef struct {
    double y_init;       /* початкова висота променя */
    double y_focal;      /* висота перетину фокальної площини */
    double intensity;    /* інтенсивність (1.0 — пройшов, 0.0 — затінений) */
    int is_lost;         /* прапорець втрати на стінці */
} RayResult;

typedef struct {
    double focal_length; /* фокусна відстань f */
    double refractive_index; /* показник заломлення n */
    double zone_pitch;   /* крок зон p */
    double draft_angle_rad; /* ухил стінки ψ у радіанах */
    int num_zones;       /* кількість кільцевих зон */
} FresnelLens;

/* Обчислення кута нахилу грані α(r) за точною формулою Снелла */
static double compute_facet_angle(double r, double f, double n) {
    double theta = atan(r / f);
    double sin_th = sin(theta);
    double cos_th = cos(theta);
    return atan2(sin_th, n - cos_th);
}

/* Трасування пучка променів крізь лінзу Френеля */
int trace_fresnel_beam(const FresnelLens *lens, int num_rays, RayResult *results) {
    if (!lens || !results || num_rays <= 0) return -1;

    double max_r = lens->num_zones * lens->zone_pitch;
    double dy = max_r / num_rays;

    for (int i = 0; i < num_rays; i++) {
        double y = (i + 0.5) * dy;
        int zone_idx = (int)(y / lens->zone_pitch);
        double r_zone = (zone_idx + 0.5) * lens->zone_pitch;
        
        double alpha = compute_facet_angle(r_zone, lens->focal_length, lens->refractive_index);
        double h_step = lens->zone_pitch * tan(alpha);

        /* Перевірка затінення стінкою канавки */
        double y_in_zone = fmod(y, lens->zone_pitch);
        double shadow_width = h_step * tan(lens->draft_angle_rad);

        results[i].y_init = y;

        if (y_in_zone > (lens->zone_pitch - shadow_width)) {
            results[i].is_lost = 1;
            results[i].intensity = 0.0;
            results[i].y_focal = 0.0;
        } else {
            results[i].is_lost = 0;
            results[i].intensity = 1.0;

            /* Векторний закон Снелла на похилій грані */
            double n_x = -sin(alpha);
            double n_y = cos(alpha);
            double cos_th1 = n_y; /* для падаючого променя (1,0) */
            double sin_th1_sq = 1.0 - cos_th1 * cos_th1;
            double sin_th2_sq = sin_th1_sq / (lens->refractive_index * lens->refractive_index);
            
            if (sin_th2_sq > 1.0) {
                /* Повне внутрішнє відбиття — виходу немає */
                results[i].is_lost = 1;
                results[i].intensity = 0.0;
                results[i].y_focal = 0.0;
                continue;
            }

            double cos_th2 = sqrt(1.0 - sin_th2_sq);
            double gamma = cos_th1 - lens->refractive_index * cos_th2;
            double rx = (1.0 / lens->refractive_index) + gamma * n_x;
            double ry = gamma * n_y;

            /* Продовження променя до фокальної площини x = f */
            double dist_x = lens->focal_length;
            results[i].y_focal = y + (ry / rx) * dist_x;
        }
    }
    return 0;
}
