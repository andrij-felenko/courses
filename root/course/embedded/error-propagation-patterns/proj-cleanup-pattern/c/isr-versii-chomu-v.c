// ESP_GOTO_ON_ERROR_ISR — те саме тіло, але «ранній» лог, безпечний в ISR:
do {
    esp_err_t err_rc_ = (x);
    if (unlikely(err_rc_ != ESP_OK)) {
        ESP_EARLY_LOGE(log_tag, "%s(%d): " format,   // ← EARLY, не звичайний LOGE
                       __FUNCTION__, __LINE__, ##__VA_ARGS__);
        ret = err_rc_;
        goto goto_tag;
    }
} while (0)
