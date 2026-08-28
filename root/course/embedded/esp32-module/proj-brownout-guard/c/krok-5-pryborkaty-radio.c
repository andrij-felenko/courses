static void wifi_apply_power_policy(uint32_t brownout_count)
{
    // Що більше brownout-ів поспіль, то скромніший апетит радіо.
    int8_t want;                 // одиниця — 0.25 dBm
    if (brownout_count == 0)      want = 78;  // 19.5 dBm — повна
    else if (brownout_count < 3)  want = 52;  // 13 dBm  — помірна
    else                          want = 34;  // 8.5 dBm — обережна

    esp_err_t err = esp_wifi_set_max_tx_power(want);   // ТІЛЬКИ після esp_wifi_start()
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "set_tx_power: %s", esp_err_to_name(err));
        return;
    }
    int8_t actual = 0;
    esp_wifi_get_max_tx_power(&actual);                 // округлене драйвером
    ESP_LOGI(TAG, "TX-потужність: хотів %.2f, стоїть %.2f dBm",
             want * 0.25, actual * 0.25);
}
