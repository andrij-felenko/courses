#include "organizer_calc.h"
#include <math.h>
#include <stdio.h>

/* Обчислення геометрії комірки з урахуванням випадкового насипання та ергономіки */
CellCalculation calc_cell_dimensions(const PartSpec *part, double packing_density, double safety_margin) {
    CellCalculation res;
    if (packing_density <= 0.05 || packing_density > 1.0) {
        packing_density = 0.58; /* Середнє значення для хаотичного насипання */
    }
    if (safety_margin < 1.0) {
        safety_margin = 1.25; /* Технологічний запас 25% на виймання пальцями */
    }

    res.part_volume_mm3 = part->length_mm * part->width_mm * part->height_mm;
    res.bulk_volume_mm3 = (res.part_volume_mm3 * (double)part->count) / packing_density;
    res.required_volume_mm3 = res.bulk_volume_mm3 * safety_margin;

    /* Пропорції комірки: глибина близько 35-45 мм для стандартного лотка */
    res.inner_height_mm = 38.0;
    double floor_area_mm2 = res.required_volume_mm3 / res.inner_height_mm;

    /* Розрахунок основи з пропорцією 4:3 або близькою до квадрата */
    res.inner_width_mm = sqrt(floor_area_mm2 * 0.75);
    if (res.inner_width_mm < part->length_mm * 1.5) {
        res.inner_width_mm = part->length_mm * 1.5;
    }
    res.inner_length_mm = floor_area_mm2 / res.inner_width_mm;
    if (res.inner_length_mm < part->length_mm * 1.5) {
        res.inner_length_mm = part->length_mm * 1.5;
    }

    /* Визначення розміру модуля Gridfinity (42 мм крок) */
    res.grid_units_x = (size_t)ceil((res.inner_width_mm + 4.0) / GRIDFINITY_PITCH_MM);
    if (res.grid_units_x == 0) res.grid_units_x = 1;
    res.grid_units_y = (size_t)ceil((res.inner_length_mm + 4.0) / GRIDFINITY_PITCH_MM);
    if (res.grid_units_y == 0) res.grid_units_y = 1;

    return res;
}

/* Розрахунок часу експоненційного розсіювання статичного заряду за IEC 61340-5-1 */
EsdCalculation calc_esd_decay(double surface_resistivity, double capacitance_pf, double v_init, double v_target) {
    EsdCalculation res;
    res.surface_resistivity_ohm_sq = surface_resistivity;
    res.capacitance_pf = capacitance_pf;
    res.initial_voltage_v = v_init;
    res.target_voltage_v = v_target;

    /* Переведення ємності з пФ у Фаради */
    double c_farad = capacitance_pf * 1.0e-12;

    /* Еквівалентний опір витоку пропорційний питомому поверхневому опору */
    double r_discharge_ohm = surface_resistivity;

    /* Постійна часу ланцюга тау = R * C */
    double tau = r_discharge_ohm * c_farad;

    if (v_init > 0.0 && v_target > 0.0 && v_init > v_target) {
        /* Формула розпаду напруги: V(t) = V0 * exp(-t / tau) => t = -tau * ln(V_target / V0) */
        res.decay_time_sec = -tau * log(v_target / v_init);
    } else {
        res.decay_time_sec = 0.0;
    }

    /* Критерій IEC 61340-5-1: час спаду заряду до 10% повинен бути <= 2.0 секунди */
    res.is_esd_safe = (res.decay_time_sec <= ESD_LIMIT_TIME_SEC) && (surface_resistivity >= 1.0e5 && surface_resistivity <= 1.0e11);

    return res;
}

/* Оптимізація матриці касетного блоку під стандартні ряди E12 або E24 */
MatrixLayout calc_optimal_matrix(ERowSeries series, double cell_w, double cell_l, double wall_th) {
    MatrixLayout res;
    res.series = series;
    res.total_compartments = (series == EROW_E12) ? 12 : 24;
    res.wall_thickness_mm = wall_th;

    /* Пошук конфігурації колонок та рядків, найближчої до співвідношення сторін 4:3 */
    size_t best_cols = res.total_compartments;
    size_t best_rows = 1;
    double min_diff = 1e9;

    for (size_t c = 1; c <= res.total_compartments; ++c) {
        if (res.total_compartments % c == 0) {
            size_t r = res.total_compartments / c;
            double w = (double)c * cell_w + (double)(c + 1) * wall_th;
            double l = (double)r * cell_l + (double)(r + 1) * wall_th;
            double ratio = w / l;
            double diff = fabs(ratio - 1.333); /* Цільове співвідношення 4:3 */
            if (diff < min_diff) {
                min_diff = diff;
                best_cols = c;
                best_rows = r;
            }
        }
    }

    res.columns = best_cols;
    res.rows = best_rows;
    res.total_width_mm = (double)best_cols * cell_w + (double)(best_cols + 1) * wall_th;
    res.total_length_mm = (double)best_rows * cell_l + (double)(best_rows + 1) * wall_th;

    return res;
}
