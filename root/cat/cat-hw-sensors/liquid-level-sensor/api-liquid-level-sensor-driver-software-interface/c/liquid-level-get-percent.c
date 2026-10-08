// Зчитування показників драйвера (C)
float liquid_level_get_percent(void) {
    float filtered_adc = process_pipeline_read();
    return calculate_percentage(filtered_adc);
}

float liquid_level_get_height_mm(void) {
    float percent = liquid_level_get_percent();
    return (percent / 100.0f) * g_config.max_height_mm;
}

float liquid_level_get_volume_liters(void) {
    float height_mm = liquid_level_get_height_mm();
    // Розрахунок для циліндричного бака радіусом R_mm
    float area_sq_mm = 3.14159f * R_mm * R_mm;
    float volume_cubic_mm = area_sq_mm * height_mm;
    return volume_cubic_mm / 1000000.0f; // Переведення куб.мм у літри
}
