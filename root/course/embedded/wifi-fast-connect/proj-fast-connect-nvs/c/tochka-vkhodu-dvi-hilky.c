static esp_netif_t *s_sta_netif;

void app_main(void)
{
    fastconn_nvs_init();
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    s_sta_netif = esp_netif_create_default_wifi_sta();

    s_wifi_events = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, &ip_event_handler, NULL, NULL));

    wifi_init_config_t wcfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&wcfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));

    // Розгалуження: є чинна заготовка → теплий старт, ні → холодний.
    fastconn_t st;
    if (fastconn_load(&st)) {
        ESP_LOGI(TAG, "warm start: ch=%u", st.channel);
        apply_sta_config(&st);          // підставляємо канал з кешу
        s_tried_warm = true;
        // Адресу веде сам стек через RESTORE_LAST_IP — DHCP лишаємо ввімкненим.
        // (Якби ми обрали статику — тут був би apply_static_ip(s_sta_netif, &st).)
    } else {
        ESP_LOGI(TAG, "cold start: full scan");
        apply_sta_config(NULL);         // channel = 0, повний скан
        s_tried_warm = false;
    }

    ESP_ERROR_CHECK(esp_wifi_start());   // звідси полетять події STA_START/...

    // Чекаємо, поки підключимося або вичерпаємо спроби.
    EventBits_t bits = xEventGroupWaitBits(
        s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
        pdFALSE, pdFALSE, pdMS_TO_TICKS(15000));

    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI(TAG, "connected — ready to work");
        // ... тут корисна робота: передати дані й заснути ...
    } else {
        ESP_LOGW(TAG, "could not connect in time");
    }
}
