    int before = measure_vdd_min_mv(adc, ch, 5, DIV_NUM, DIV_DEN);   // спокій
    esp_wifi_start();
    esp_wifi_connect();
    int during = measure_vdd_min_mv(adc, ch, 300, DIV_NUM, DIV_DEN); // під час старту радіо

    ESP_LOGI(TAG, "3V3: спокій %d мВ, провал при старті радіо %d мВ (поріг BOD ≈ %d мВ)",
             before, during, brownout_threshold_mv());
    if (during < brownout_threshold_mv() + 150) {
        ESP_LOGW(TAG, "провал майже дістає порога — живлення на межі, тре товщу розв'язку");
    }
