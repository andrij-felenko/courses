// Захоплення та обробка кадру у завданні FreeRTOS
void capture_task(void *pvParameters) {
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        // Обробка помилки ініціалізації
        vTaskDelete(NULL);
    }

    while (1) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            // Не вдалося отримати буфер кадру
            continue;
        }

        // Робота з даними кадру: fb->buf, fb->len

        // Обов'язкове повернення буфера драйверу
        esp_camera_fb_return(fb);
    }
}
