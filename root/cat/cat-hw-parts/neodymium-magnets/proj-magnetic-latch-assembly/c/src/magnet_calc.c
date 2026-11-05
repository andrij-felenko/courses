#include "magnet_calc.h"
#include <math.h>
#include <stddef.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Магнітна стала вакууму mu0 = 4*pi*1e-7 Гн/м */
#define MU_0 (4.0 * M_PI * 1e-7)

double calc_pole_area_mm2(double diameter_mm) {
    if (diameter_mm <= 0.0) {
        return 0.0;
    }
    double radius = diameter_mm / 2.0;
    return M_PI * radius * radius;
}

double calc_axial_flux_density(const DiscMagnet *magnet, double air_gap_mm) {
    if (!magnet || magnet->diameter_mm <= 0.0 || magnet->thickness_mm <= 0.0 || magnet->br_tesla <= 0.0) {
        return 0.0;
    }

    double r = magnet->diameter_mm / 2.0;
    double l = magnet->thickness_mm;
    double z = (air_gap_mm < 0.0) ? 0.0 : air_gap_mm;

    /*
     * Аналітична модель поля циліндричного постійного магніту на центральній осі:
     * B(z) = (Br / 2) * [ (z + l) / sqrt(r^2 + (z + l)^2) - z / sqrt(r^2 + z^2) ]
     */
    double term1 = (z + l) / sqrt(r * r + (z + l) * (z + l));
    double term2 = (z == 0.0) ? 0.0 : (z / sqrt(r * r + z * z));

    return (magnet->br_tesla / 2.0) * (term1 - term2);
}

double calc_maxwell_pull_force_n(double b_tesla, double pole_area_mm2) {
    if (b_tesla <= 0.0 || pole_area_mm2 <= 0.0) {
        return 0.0;
    }

    /*
     * Формула Максвелла для тягового зусилля магнітного полюса:
     * F = (B^2 * A) / (2 * mu0)
     * де A переводиться з мм² у м² (множник 1e-6)
     */
    double area_m2 = pole_area_mm2 * 1e-6;
    return (b_tesla * b_tesla * area_m2) / (2.0 * MU_0);
}

bool evaluate_magnet_latch(const DiscMagnet *magnet,
                          const PocketFit *fit,
                          const CoverLatchConfig *latch,
                          double air_gap_mm,
                          LatchReport *out_report) {
    if (!magnet || !fit || !latch || !out_report) {
        return false;
    }

    out_report->pole_area_mm2 = calc_pole_area_mm2(magnet->diameter_mm);
    out_report->b_surface_tesla = calc_axial_flux_density(magnet, air_gap_mm);
    out_report->pull_force_n = calc_maxwell_pull_force_n(out_report->b_surface_tesla, out_report->pole_area_mm2);

    /* Зсувне зусилля пропорційне нормальній силі притискання через коефіцієнт тертя */
    out_report->shear_force_n = out_report->pull_force_n * latch->friction_coeff;

    /*
     * Площа клейового контакту у циліндричному гнізді:
     * торцева донна поверхня + циліндрична бічна стінка заглибленої частини
     */
    double base_area = out_report->pole_area_mm2;
    double side_area = M_PI * magnet->diameter_mm * fit->pocket_depth_mm;
    out_report->glue_area_mm2 = base_area + side_area;

    /*
     * Напруження в клейовому шві при спробі відриву магніту від гнізда:
     * tau = F_pull / A_glue (у МПа = Н/мм²)
     */
    if (out_report->glue_area_mm2 > 0.0) {
        out_report->glue_shear_stress_mpa = out_report->pull_force_n / out_report->glue_area_mm2;
    } else {
        out_report->glue_shear_stress_mpa = 0.0;
    }

    /* Коефіцієнт запасу міцності клейового шва */
    if (out_report->glue_shear_stress_mpa > 1e-6) {
        out_report->safety_factor = fit->glue_shear_strength_mpa / out_report->glue_shear_stress_mpa;
    } else {
        out_report->safety_factor = 999.0;
    }

    /* Безпечним вважається запас міцності >= 2.0 */
    out_report->is_glue_safe = (out_report->safety_factor >= 2.0);

    /*
     * Зусилля відкривання на ручці за правилом важеля:
     * M = F_pull * L_magnet = F_open * L_handle
     * F_open = F_pull * (L_magnet / L_handle)
     */
    if (latch->handle_arm_mm > 0.0) {
        out_report->opening_force_n = out_report->pull_force_n * (latch->magnet_arm_mm / latch->handle_arm_mm);
    } else {
        out_report->opening_force_n = out_report->pull_force_n;
    }

    return true;
}
