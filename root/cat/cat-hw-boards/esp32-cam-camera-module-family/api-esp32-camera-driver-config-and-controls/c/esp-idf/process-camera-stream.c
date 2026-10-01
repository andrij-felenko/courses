void process_camera_stream(void) {
    while (1) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE("CAM", "Захоплення кадру не вдалося");
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // Обробка або трансляція кадру
        ESP_LOGI("CAM", "Отримано кадр: %u × %u, розмір: %u Байт",
                 fb->width, fb->height, fb->len);

        // Обов'язкове повернення кадрового буфера в пул
        esp_camera_fb_return(fb);

        vTaskDelay(pdMS_TO_TICKS(30));
    }
}
