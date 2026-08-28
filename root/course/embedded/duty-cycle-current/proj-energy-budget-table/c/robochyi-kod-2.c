void report_battery_life(void) {
    static const phase_t cycle[] = {
        { 120000u, 1200000u },   // boot + Wi-Fi конект: 120 мА, 1.2 с
        {  25000u,  200000u },   // вимір:                25 мА, 0.2 с
        { 180000u,  300000u },   // TX:                  180 мА, 0.3 с
    };
    budget_t b = energy_budget(cycle, sizeof(cycle)/sizeof(cycle[0]),
                               600ull * 1000000ull,  // період 600 с у мкс
                               8u,                    // сон 8 мкА
                               2000u);                // батарея 2000 мА·год

    // Очікувано: avg ≈ 346 мкА, life ≈ 5775 год (≈ 8 місяців).
    ESP_LOGI("pwr", "I_сер = %u мкА; залишок ≈ %u год (%u діб)",
             b.avg_current_uA, b.life_hours, b.life_hours / 24);
}
