esp_err_t err = esp_camera_init(&config);
if (err != ESP_OK) {
    Serial.printf("Помилка ініціалізації камери: 0x%x\n", err);
    return;
}

camera_fb_t *fb = esp_camera_fb_get();
if (!fb) {
    Serial.println("Помилка захоплення кадру");
    return;
}

// Використання даних fb->buf

esp_camera_fb_return(fb);
