void app_main(void) {
    esp_reset_reason_t reason = esp_reset_reason();
    if (reason == ESP_RST_PANIC) {
        size_t addr = 0, size = 0;
        if (esp_core_dump_image_get(&addr, &size) == ESP_OK) {
            ESP_LOGE("boot", "panic reboot, core dump %u B at 0x%x", size, addr);
            // підняти прапор у NVS: «є свіжий дамп, забери при нагоді»
        }
    }
    // ... звичайний старт
}
