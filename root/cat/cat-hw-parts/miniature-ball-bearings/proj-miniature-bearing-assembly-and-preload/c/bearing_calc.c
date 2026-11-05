#include "bearing_calc.h"

#define STEEL_E_MPA 210000.0

double calc_contact_pressure_mpa(double d_shaft_mm, double interference_um, double ring_wall_mm) {
    if (d_shaft_mm <= 0.0 || interference_um <= 0.0 || ring_wall_mm <= 0.0) {
        return 0.0;
    }
    double delta_mm = interference_um / 1000.0;
    double d_outer_ring_mm = d_shaft_mm + 2.0 * ring_wall_mm;
    double k = d_shaft_mm / d_outer_ring_mm;
    return (STEEL_E_MPA * delta_mm / (2.0 * d_shaft_mm)) * (1.0 - k * k);
}

double calc_press_force_n(double d_shaft_mm, double width_mm, double pressure_mpa, double friction_coeff) {
    if (d_shaft_mm <= 0.0 || width_mm <= 0.0 || pressure_mpa <= 0.0 || friction_coeff <= 0.0) {
        return 0.0;
    }
    return 3.141592653589793 * d_shaft_mm * width_mm * pressure_mpa * friction_coeff;
}

double calc_wave_spring_force_n(const WaveSpringParams *spring) {
    if (!spring || spring->work_height_mm >= spring->free_height_mm) {
        return 0.0;
    }
    return (spring->free_height_mm - spring->work_height_mm) * spring->spring_rate_n_mm;
}

bool calculate_assembly(const BearingParams *bearing,
                        const PressFitParams *fit,
                        const WaveSpringParams *spring,
                        AssemblyReport *out_report) {
    if (!bearing || !fit || !spring || !out_report) {
        return false;
    }

    double ring_wall_mm = (bearing->d_outer_mm - bearing->d_inner_mm) * 0.25;
    if (ring_wall_mm <= 0.5) {
        ring_wall_mm = 0.8;
    }

    out_report->contact_pressure_mpa = calc_contact_pressure_mpa(bearing->d_inner_mm, fit->shaft_interference_um, ring_wall_mm);
    out_report->press_force_n = calc_press_force_n(bearing->d_inner_mm, bearing->width_mm, out_report->contact_pressure_mpa, fit->friction_coeff);
    out_report->preload_force_n = calc_wave_spring_force_n(spring);
    out_report->preload_min_rec_n = bearing->c0_stat_n * 0.005;
    out_report->preload_max_rec_n = bearing->c0_stat_n * 0.020;
    out_report->preload_is_safe = (out_report->preload_force_n >= out_report->preload_min_rec_n &&
                                   out_report->preload_force_n <= out_report->preload_max_rec_n);
    return true;
}
