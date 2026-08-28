#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846
#define EPSILON_0 8.854187817e-12
#define MU_0 (4.0 * PI * 1e-7)
#define COPPER_RESISTIVITY 1.72e-8

typedef struct {
    double dielectric_height_mm;
    double relative_permittivity;
    double trace_width_mm;
    double trace_thickness_um;
    double trace_length_mm;
} MicrostripParams;

typedef struct {
    double slot_length_mm;
    double slot_width_mm;
} GroundSlotParams;

double calc_current_density(double x_mm, double h_mm, double current_a) {
    double h = h_mm * 1e-3;
    double x = x_mm * 1e-3;
    double peak_density = current_a / (PI * h);
    double factor = 1.0 / (1.0 + (x / h) * (x / h));
    return peak_density * factor;
}

double calc_current_fraction_in_band(double x_boundary_mm, double h_mm) {
    double ratio = x_boundary_mm / h_mm;
    return (2.0 / PI) * atan(ratio);
}

double calc_crossover_frequency(const MicrostripParams *p) {
    double w_m = p->trace_width_mm * 1e-3;
    double t_m = p->trace_thickness_um * 1e-6;
    double l_m = p->trace_length_mm * 1e-3;
    double h_m = p->dielectric_height_mm * 1e-3;

    double area_m2 = w_m * t_m;
    double r_dc = COPPER_RESISTIVITY * l_m / area_m2;

    double z0 = (87.0 / sqrt(p->relative_permittivity + 1.41)) *
                log(5.98 * h_m / (0.8 * w_m + t_m));
    double v_prop = 3e8 / sqrt(p->relative_permittivity);
    double l_loop = (z0 / v_prop) * l_m;

    return r_dc / (2.0 * PI * l_loop);
}

double calc_slot_inductance(const GroundSlotParams *s) {
    double l_m = s->slot_length_mm * 1e-3;
    double w_m = s->slot_width_mm * 1e-3;
    if (w_m <= 0.0 || l_m <= w_m) return 0.0;
    return MU_0 * l_m * log(l_m / w_m);
}

double calc_radiated_emissions(double freq_hz, double current_a, double loop_area_m2, double dist_m) {
    return 1.316e-14 * (freq_hz * freq_hz * current_a * loop_area_m2) / dist_m;
}

double calc_plane_capacitance(double area_cm2, double thickness_um, double eps_r) {
    double area_m2 = area_cm2 * 1e-4;
    double d_m = thickness_um * 1e-6;
    return (EPSILON_0 * eps_r * area_m2) / d_m;
}

int main(void) {
    MicrostripParams trace = {
        .dielectric_height_mm = 0.12,
        .relative_permittivity = 4.3,
        .trace_width_mm = 0.22,
        .trace_thickness_um = 35.0,
        .trace_length_mm = 60.0
    };

    printf("=== АНАЛІЗ ОПОРНОГО ШАРУ ЗЕМЛІ (C99) ===\n\n");

    printf("1. Розподіл густини зворотного струму під доріжкою (h = %.2f мм, I = 1.0 A):\n", trace.dielectric_height_mm);
    printf("   x = 0.00 мм (пік):     J = %8.2f А/м  (100.0%%)\n", calc_current_density(0.0, trace.dielectric_height_mm, 1.0));
    printf("   x = ±h (±0.12 мм):     J = %8.2f А/м  (частка в смузі: %.1f%%)\n",
           calc_current_density(trace.dielectric_height_mm, trace.dielectric_height_mm, 1.0),
           calc_current_fraction_in_band(trace.dielectric_height_mm, trace.dielectric_height_mm) * 100.0);
    printf("   x = ±3h (±0.36 мм):    J = %8.2f А/м  (частка в смузі: %.1f%%)\n",
           calc_current_density(3.0 * trace.dielectric_height_mm, trace.dielectric_height_mm, 1.0),
           calc_current_fraction_in_band(3.0 * trace.dielectric_height_mm, trace.dielectric_height_mm) * 100.0);
    printf("   x = ±10h (±1.20 мм):   J = %8.2f А/м  (частка в смузі: %.1f%%)\n\n",
           calc_current_density(10.0 * trace.dielectric_height_mm, trace.dielectric_height_mm, 1.0),
           calc_current_fraction_in_band(10.0 * trace.dielectric_height_mm, trace.dielectric_height_mm) * 100.0);

    double fc = calc_crossover_frequency(&trace);
    printf("2. Частота кросоверу опір/індуктивність: f_c = %.2f кГц\n\n", fc / 1000.0);

    GroundSlotParams slot = { .slot_length_mm = 12.0, .slot_width_mm = 0.5 };
    double l_slot = calc_slot_inductance(&slot);
    double di_dt = 0.025 / 0.6e-9;
    double v_bounce = l_slot * di_dt;

    printf("3. Паразитна індуктивність розрізу (L = %.1f мм, W = %.1f мм):\n", slot.slot_length_mm, slot.slot_width_mm);
    printf("   L_slot = %.2f нГн\n", l_slot * 1e9);
    printf("   Ground bounce стрибок (dI = 25 мА, dt = 600 пс): V_bounce = %.3f В\n\n", v_bounce);

    double area_continuous = (trace.trace_length_mm * 1e-3) * (trace.dielectric_height_mm * 1e-3);
    double area_slotted = area_continuous + (slot.slot_length_mm * 1e-3) * 0.015;
    double e_clean = calc_radiated_emissions(200e6, 0.025, area_continuous, 3.0);
    double e_slotted = calc_radiated_emissions(200e6, 0.025, area_slotted, 3.0);

    printf("4. Випромінювання на 200 МГц (відстань 3 м):\n");
    printf("   Нерозривний шар GND:   E = %8.3f мкВ/м (%6.2f дБмкВ/м)\n", e_clean * 1e6, 20.0 * log10(e_clean * 1e6));
    printf("   Перетин розрізу землі: E = %8.3f мкВ/м (%6.2f дБмкВ/м)\n", e_slotted * 1e6, 20.0 * log10(e_slotted * 1e6));
    printf("   Перевищення емісії:    Δ = +%.1f дБ\n\n", 20.0 * log10(e_slotted / e_clean));

    double c_pdn = calc_plane_capacitance(60.0, 75.0, 4.3);
    printf("5. Міжшарова ємність живлення-земля (60 см², d = 75 мкм): C = %.2f нФ\n", c_pdn * 1e9);

    return 0;
}
