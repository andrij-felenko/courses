int main() {
    using namespace sealing;
    GasketParameters cfg{
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

    auto eval = EnclosureSealingCalculator::calculate(cfg);
    if (!eval) {
        std::cerr << "Помилка вхідних параметрів розрахунку!\n";
        return 1;
    }

    const auto& res = *eval;
    std::cout << std::format("--- РЕЗУЛЬТАТИ РОЗРАХУНКУ УЩІЛЬНЕННЯ IP67 ---\n");
    std::cout << std::format("Ступінь стиснення:        {:.2f} %  [{}]\n", res.compression_pct, res.is_compression_valid() ? "OK" : "ПОМИЛКА");
    std::cout << std::format("Заповнення паза:          {:.2f} %  [{}]\n", res.gland_fill_pct, res.is_fill_valid() ? "OK" : "ПОМИЛКА");
    std::cout << std::format("Погонна сила стиснення:   {:.2f} Н/мм\n", res.linear_force_n_per_mm);
    std::cout << std::format("Сумарна сила притискання: {:.1f} Н ({:.1f} кгс)\n", res.total_force_n, res.total_force_n / 9.81);
    std::cout << std::format("Зусилля на 1 гвинт:       {:.1f} Н\n", res.bolt_force_n);
    std::cout << std::format("Прогин фланця між гвинтами: {:.4f} мм (ліміт: {:.4f} мм) [{}]\n",
                             res.flange_deflection_mm, res.max_allowed_deflection_mm, res.is_deflection_valid() ? "OK" : "ПОМИЛКА");
    std::cout << std::format("Термічний вакуум:         -{:.2f} кПа (-{:.0f} мбар)\n", res.thermal_vacuum_kpa, res.thermal_vacuum_kpa * 10.0);
    std::cout << std::format("Потрібний потік повітря:  {:.1f} мл/хв\n", res.airflow_req_ml_min);
    
    const double vent_diameter_mm = 2.0 * std::sqrt(res.min_vent_area_cm2 / std::numbers::pi) * 10.0;
    std::cout << std::format("Мін. площа ePTFE-мембрани: {:.3f} см^2 (діаметр >= {:.1f} мм)\n",
                             res.min_vent_area_cm2, vent_diameter_mm);
    std::cout << std::format("ЗАГАЛЬНИЙ ВИСНОВОК:       {}\n", res.is_pass() ? "КОНСТРУКЦІЯ НАДІЙНА" : "ПОТРІБНЕ ДООПРАЦЮВАННЯ");

    return 0;
}
