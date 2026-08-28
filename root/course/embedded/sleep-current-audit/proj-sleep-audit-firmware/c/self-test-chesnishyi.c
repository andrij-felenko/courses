void sleep_self_test_auto(void)
{
    const TickType_t SETTLE = pdMS_TO_TICKS(500);

    apply_sleep_profile();
    all_branches_off();
    vTaskDelay(SETTLE);
    float floor_uA = power_monitor_read_uA();      // підлога: сам чип
    ESP_LOGI("AUDIT", "підлога (сам чип): %.1f мкА", floor_uA);

    for (size_t i = 0; i < BRANCH_LEN; i++) {
        all_branches_off();
        gpio_set_level(BRANCHES[i].en_pin, 1);
        vTaskDelay(SETTLE);
        float total = power_monitor_read_uA();
        ESP_LOGI("AUDIT", "гілка '%-8s': %.1f мкА  (внесок %.1f мкА)",
                 BRANCHES[i].name, total, total - floor_uA);
    }
    all_branches_off();
}
