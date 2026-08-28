// Записане базове число — оновлюємо ВРУЧНУ лише коли аудит свідомо зійшовся.
#define SLEEP_BASELINE_UA   26.0f    // зняте після фіксу (див. worked-приклад статті)
#define SLEEP_TOLERANCE_UA  10.0f    // допуск на розкид плат/температуру

// Режим аудиту: завести в сон, зняти струм, звірити з baseline.
void assert_sleep_baseline(void)
{
    apply_sleep_profile();
    sensor_power_down();
    display_power_down();
    radio_power_down();
    vTaskDelay(pdMS_TO_TICKS(1000));     // дати струму усталитися

    float now = power_monitor_read_uA();
    if (now > SLEEP_BASELINE_UA + SLEEP_TOLERANCE_UA) {
        ESP_LOGE("AUDIT", "РЕГРЕСІЯ струму спокою: %.1f мкА проти baseline %.1f мкА "
                          "(+%.1f). Хтось лишив ніжку в HIGH?",
                 now, SLEEP_BASELINE_UA, now - SLEEP_BASELINE_UA);
    } else {
        ESP_LOGI("AUDIT", "струм спокою OK: %.1f мкА (baseline %.1f)",
                 now, SLEEP_BASELINE_UA);
    }
}
