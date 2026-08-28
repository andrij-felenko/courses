void app_main(void)
{
    esp_reset_reason_t reason = esp_reset_reason();
    brownout_bookkeeping(reason);                 // полічити (крок 2)
    ESP_LOGI(TAG, "поріг BOD ≈ %d мВ", brownout_threshold_mv());  // (крок 3)

    // …ініціалізація NVS, netif, event loop…

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));

    // Стартуємо радіо СКРОМНО, щоб приборкати перший сплеск PA:
    ESP_ERROR_CHECK(esp_wifi_start());            // тепер set/get_tx_power дозволені
    wifi_apply_power_policy(s_brownout_count);     // (крок 5)

    ESP_ERROR_CHECK(esp_wifi_connect());          // аж тепер — у ефір
}
