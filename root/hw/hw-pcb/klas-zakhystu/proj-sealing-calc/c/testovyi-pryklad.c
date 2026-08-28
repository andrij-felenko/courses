int main(void) {
    GasketInput cfg = {
        .cord_diameter_mm = 2.5,
        .gland_width_mm = 3.4,
        .gland_depth_mm = 1.9,
        .perimeter_mm = 500.0,
        .bolt_spacing_mm = 45.0,
        .flange_thickness_mm = 3.0,
        .flange_width_mm = 8.0,
        .shore_a = 70.0,
        .mat_young_modulus_mpa = 70000.0,
        .internal_volume_l = 1.2,
        .temp_hot_c = 65.0,
        .temp_cold_c = 10.0,
        .target_time_sec = 60.0,
        .vent_permeability = 400.0
    };

    GasketResult res;
    if (calculate_gasket_seal(&cfg, &res)) {
        printf("--- РЕЗУЛЬТАТИ РОЗРАХУНКУ УЩІЛЬНЕННЯ IP67 ---\n");
        printf("Ступінь стиснення:        %.2f %%  [%s]\n", res.compression_ratio_pct, res.is_compression_ok ? "OK" : "ПОМИЛКА");
        printf("Заповнення паза:          %.2f %%  [%s]\n", res.gland_fill_pct, res.is_fill_ok ? "OK" : "ПОМИЛКА");
        printf("Погонна сила стиснення:   %.2f Н/мм\n", res.linear_force_n_per_mm);
        printf("Сумарна сила притискання: %.1f Н (%.1f кгс)\n", res.total_clamp_force_n, res.total_clamp_force_n / 9.81);
        printf("Зусилля на 1 гвинт:       %.1f Н\n", res.bolt_force_n);
        printf("Прогин фланця між гвинтами: %.4f мм (макс допустимий: %.4f мм) [%s]\n",
               res.flange_deflection_mm, res.max_allowable_defl_mm, res.is_deflection_ok ? "OK" : "ПОМИЛКА");
        printf("Термічний вакуум:         -%.2f кПа (-%.0f мбар)\n", res.thermal_vacuum_kpa, res.thermal_vacuum_kpa * 10.0);
        printf("Потрібний потік повітря:  %.1f мл/хв\n", res.required_airflow_ml_min);
        printf("Мін. площа ePTFE-мембрани: %.3f см^2 (діаметр >= %.1f мм)\n",
               res.min_vent_area_cm2, 2.0 * sqrt(res.min_vent_area_cm2 / M_PI) * 10.0);
        printf("ЗАГАЛЬНИЙ ВИСНОВОК:       %s\n", res.is_design_valid ? "КОНСТРУКЦІЯ НАДІЙНА" : "ПОТРІБНЕ ДООПРАЦЮВАННЯ");
    }
    return 0;
}
